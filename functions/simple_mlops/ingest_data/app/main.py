import os

import functions_framework
from cloudevents.http import CloudEvent
from google.cloud import bigquery, pubsub, storage

try:
    from _modules import _gcp_apis as gcp_apis
    from _modules import _models as models
    from _modules import _transform as transform
except ImportError:
    from functions.simple_mlops.ingest_data.app._modules import _gcp_apis as gcp_apis
    from functions.simple_mlops.ingest_data.app._modules import _models as models
    from functions.simple_mlops.ingest_data.app._modules import _transform as transform

################
# 1. Clients ###
################


def load_clients(
    gcp_project_id: str
) -> models.GCPClients:
    """Load the GCP clients.

    Args:
        gcp_project_id (str): The GCP project ID.

    Returns:
        GCPClients: A tuple of GCP clients.
            With the following attributes:
                storage_client: A storage client.
                bigquery_client: A bigquery client.
                publisher: A pubsub publisher client.
    """

    storage_client = storage.Client(project=gcp_project_id)
    bigquery_client = bigquery.Client(project=gcp_project_id)
    publisher = pubsub.PublisherClient()

    return models.GCPClients(
        storage_client=storage_client,
        bigquery_client=bigquery_client,
        publisher=publisher
    )


##############################
# 2. Environment variables ###
##############################


def _env_vars() -> models.EnvVars:
    # fqdn = fully qualified domain name
    # A table fqdn is in the format: project_id.dataset_id.table_id

    return models.EnvVars(
        gcp_project_id=os.getenv("_GCP_PROJECT_ID", 'gcp_project_id'),
        bq_table_fqdn=f'''{os.getenv("_GCP_PROJECT_ID", "gcp_project_id")}.\
{os.getenv("_BIGQUERY_DATASET_ID", "bq_table_fqdn_dst")}.\
{os.getenv("_BIGQUERY_TABLE_ID", "bq_table_fqdn_tbl")}''',
        topic_ingestion_complete=os.getenv(
            "TOPIC_INGESTION_COMPLETE", 'topic_ingestion_complete')
    )


if __name__ == "__main__":
    gcp_clients = load_clients(gcp_project_id="Your Project ID")
    env_vars = _env_vars()


@functions_framework.cloud_event
def main(cloud_event: CloudEvent) -> None:
    """Entrypoint of the cloud function.

    Args:
        cloud_event (CloudEvent): The cloud event that triggered this function.
    """
    # Get the event data
    print(cloud_event.get_data())

    data = cloud_event.get_data()

    #########################################################
    # 3. Correct the arguments below to download the file ###
    #########################################################
    file_contents = gcp_apis.storage_download_blob_as_string(
        CS=gcp_clients.storage_client,
        bucket_name=data['bucket'],
        file_path=data['name']
    )
    print(file_contents)

    # Split the content by lines
    datapoints = transform.split_lines(content=file_contents)

    # Get the headers (column names) from the first line
    has_headers = True
    if has_headers:
        datapoints = datapoints[1:]

    ###############################################################
    # 4. Correct the arguments below to insert data into bigquery #
    ###############################################################
    # Iterate through the the datapoints and insert them into BigQuery
    errors = [
        gcp_apis.bigquery_insert_json_row(
            BQ=gcp_clients.bigquery_client,
            table_fqdn=env_vars.bq_table_fqdn,
            row=[datapoint]
        ) for datapoint in transform.titanic_transform(datapoints=datapoints)]

    if any(errors):
        raise ValueError(f"Errors found: {errors}")

    #################################################################
    # 5. Correct the arguments below to publish a message to pubsub #
    #################################################################
    gcp_apis.pubsub_publish_message(
        PS=gcp_clients.publisher,
        project_id=env_vars.gcp_project_id,
        topic_id=env_vars.topic_ingestion_complete,
        data=f"I finished ingesting the file {data['name']}!!",
        attributes={'train_model': 'True'},
    )
