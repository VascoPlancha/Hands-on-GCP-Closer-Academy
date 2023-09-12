"""Models for the ingest_data function. Simplifies type hinting."""
from typing import NamedTuple

from google.cloud import bigquery, pubsub, storage


class GCPClients(NamedTuple):
    storage_client: storage.Client
    bigquery_client: bigquery.Client
    publisher: pubsub.PublisherClient
