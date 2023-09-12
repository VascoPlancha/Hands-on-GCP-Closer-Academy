"""Models for the ingest_data function. Simplifies type hinting."""
from typing import NamedTuple

from google.cloud import bigquery, pubsub, storage


class GCPClients(NamedTuple):
    storage_client: storage.Client
    bigquery_client: bigquery.Client
    publisher: pubsub.PublisherClient


class EnvVars(NamedTuple):
    gcp_project_id: str
    bq_table_fqdn: str
    topic_training_complete: str
