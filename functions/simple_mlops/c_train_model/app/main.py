import os
from pathlib import Path

import functions_framework
from cloudevents.http import CloudEvent
from google.cloud import bigquery, pubsub, storage

try:
    from funcs import common, gcp_apis, models, train_models
except ImportError:
    from functions.simple_mlops.c_train_model.app.funcs import (
        common,
        gcp_apis,
        models,
        train_models,
    )


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


def _env_vars() -> models.EnvVars:
    """Load the environment variables.

    This function loads the environment variables required for the application to run. It returns a tuple of environment variables.

    Returns:
        models.EnvVars: A tuple of environment variables.
    """
    # fqn = fully qualified name
    # A table fqn is in the format: project_id.dataset_id.table_id

    return models.EnvVars(
        gcp_project_id=os.getenv("_GCP_PROJECT_ID", 'gcp_project_id'),
        bq_table_fqn=f'''{os.getenv("_GCP_PROJECT_ID", "gcp_project_id")}.\
{os.getenv("_BIGQUERY_DATASET_ID", "bq_table_fqn_dst")}.\
{os.getenv("_BIGQUERY_TABLE_ID", "bq_table_fqn_tbl")}''',
        topic_training_complete=os.getenv(
            "TOPIC_TRAINING_COMPLETE", 'topic_training_complete')
    )


env_vars = _env_vars()
gcp_clients = load_clients(gcp_project_id=env_vars.gcp_project_id)


@functions_framework.cloud_event
def main(cloud_event: CloudEvent) -> None:
    """Entrypoint of the cloud function."""
    print(cloud_event)
    event_data = cloud_event.get_data()['message']

    # Train the model
    if event_data['attributes']['train_model'] == 'True':

        path = Path('./resources/select_train_data.sql')
        query = common.query_train_data(
            table_fqn='gcp_project_id.bq_table_fqn',
            path=path
        )
        df = gcp_apis.query_to_pandas_dataframe(
            query=query,
            BQ=gcp_clients.bigquery_client)

        pipeline = train_models.titanic_train(
            df=df,
        )

        gcp_apis.model_save_to_storage(
            CS=gcp_clients.storage_client,
            model=pipeline
        )
