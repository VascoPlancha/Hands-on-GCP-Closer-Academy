import os
from pathlib import Path

import functions_framework
from cloudevents.http import CloudEvent
from google.cloud import bigquery, pubsub

try:
    from funcs import common, gcp_apis, models
except ImportError:
    from functions.simple_mlops.b_update_facts.app.funcs import (
        common,
        gcp_apis,
        models,
    )

##############################################
# 0. Create the necessary resources in GCP ###
##############################################

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

    bigquery_client = bigquery.Client(project=gcp_project_id)
    publisher = pubsub.PublisherClient()

    return models.GCPClients(
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
        bq_staging_table_fqdn=f'''{os.getenv("_GCP_PROJECT_ID", "gcp_project_id")}.\
{os.getenv("_BIGQUERY_DATASET_ID", "bq_table_staging_dst")}.\
{os.getenv("_BIGQUERY_STAGING_TABLE_ID", "bq_staging_table_fqdn")}''',
        bq_facts_table_fqdn=f'''{os.getenv("_GCP_PROJECT_ID", "gcp_project_id")}.\
{os.getenv("_BIGQUERY_DATASET_ID", "bq_table_fqdn_dst")}.\
{os.getenv("_BIGQUERY_FACTS_TABLE_ID", "bq_facts_table_fqdn")}''',
        topic_update_facts_complete=os.getenv(
            "_TOPIC_UPDATE_FACTS_COMPLETE", 'topic_update_facts_complete')
    )


env_vars = _env_vars()
gcp_clients = load_clients(gcp_project_id=env_vars.gcp_project_id)


@functions_framework.cloud_event
def main(cloud_event: CloudEvent) -> None:
    """Entrypoint of the cloud function.

    Args:
        cloud_event (CloudEvent): The cloud event that triggered this function.
    """
    # Get the data from the cloud event
    data = cloud_event.get_data()
    print(data)

    #################################################
    # 3. Send the correct arguments to load_query ###
    #################################################

    path = Path('./resources/staging_to_facts.sql')

    query = common.load_query(
        table_facts=env_vars.bq_facts_table_fqdn,
        table_raw=env_vars.bq_staging_table_fqdn,
        query_path=path,
    )

    #################################################
    # 4. Send the correct arguments execute query ###
    #################################################

    _ = gcp_apis.execute_query_result(
        BQ=gcp_clients.bigquery_client,
        query=query
    )

    #################################################################
    # 5. Correct the arguments below to publish a message to pubsub #
    #################################################################
    gcp_apis.pubsub_publish_message(
        PS=gcp_clients.publisher,
        project_id=env_vars.gcp_project_id,
        topic_id=env_vars.topic_update_facts_complete,
        message="I finished passing the staging data to facts",
        attributes={
            'train_model': 'True',
            'dataset': 'titanic'},
    )
