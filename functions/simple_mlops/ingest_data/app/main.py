import os

import functions_framework
import m_gcp_apis as gcp_apis
from cloudevents.http import CloudEvent
from google.cloud import bigquery, pubsub, storage

from . import id_models as models
from . import id_transform as transform

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


gcp_clients = load_clients(gcp_project_id="Your Project ID")

##############################
# 2. Environment variables ###
##############################


def _env_vars() -> models.EnvVars:
    return models.EnvVars(
        gcp_project_id=os.getenv("_GCP_PROJECT_ID", 'error'),
        bq_dataset_id=os.getenv("_BIGQUERY_DATASET_ID", 'error'),
        bq_table_id=os.getenv("_BIGQUERY_TABLE_ID", 'error'),
        topic_ingestion_complete=os.getenv("TOPIC_INGESTION_COMPLETE", 'error')
    )


env_vars = _env_vars()


@functions_framework.cloud_event
def main(cloud_event: CloudEvent) -> None:
    """Entrypoint of the cloud function.

    Args:
        cloud_event (CloudEvent): The cloud event that triggered this function.
    """
    # Get the event data
    print(cloud_event)

    #########################################################
    # 3. Correct the arguments below to download the file ###
    #########################################################
    file_contents = gcp_apis.storage_download_blob_as_string(
        CS=gcp_clients.storage_client,
        bucket_name=cloud_event['bucket'],
        file_path=cloud_event['name']
    )
    print(file_contents)

    # Split the content by lines
    datapoints = transform.split_lines(content=file_contents)

    # Get the headers (column names) from the first line
    has_headers = True
    if has_headers:
        datapoints = datapoints[1:]

#     # # Iterate through the rest of the lines (the data points)
#     # for datapoint in lines[1:]:
#     #     errors = bigquery_client._(  # IMPLEMENTATION [5]: Find the correct method to use here
#     #         table=f"{dataset_id}.",
#     #         json_rows=[_transform_datapoint_into_dictionary(
#     #             headers=headers,
#     #             datapoint=datapoint)],
#     #     )
#     #     if errors:
#     #         print(json.dumps({
#     #             "message": "Encountered errors while inserting row",
#     #             "errors": errors,
#     #             'data': _transform_datapoint_into_dictionary(
#     #                 headers=headers,
#     #                 datapoint=datapoint),
#     #             "severity": "ERROR",
#     #         }
#
#
# ))


#     # # Publish the message
#     # # Define the topic path, it's a string "projects/[PROJECT_ID]/topics/[TOPIC_ID]"
#     # # but the `topic_path` method helps us.
#     # topic_path: str = publisher.topic_path(
#     #     project_id, topic_ingestion_complete)
#     # data = f"I finished ingesting the file {event_data['name']}!!"

#     # # Publish the message
#     # # publish_future = # IMPLEMENTATION [6]: Find the correct method with the PublisherClient to publish a message
