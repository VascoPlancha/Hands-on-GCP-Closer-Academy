from typing import NamedTuple
from google.cloud import pubsub_v1, bigquery, storage

# https://cloud.google.com/functions/docs/samples/functions-tips-lazy-globals
class GCPClients(NamedTuple):
    storage_client: storage.Client
    bigquery_client: bigquery.Client
    publisher: pubsub_v1.PublisherClient

def load_clients(
    gcp_project_id: str
) -> GCPClients:
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
    publisher = pubsub_v1.PublisherClient()

    return GCPClients(
        storage_client=storage_client,
        bigquery_client=bigquery_client,
        publisher=publisher
    )