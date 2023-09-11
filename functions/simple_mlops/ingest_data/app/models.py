"""Models for the ingest_data function."""
from typing import NamedTuple
from google.cloud import  storage, bigquery, pubsub

class GCPClients(NamedTuple):
    storage_client: storage.Client
    bigquery_client: bigquery.Client
    publisher: pubsub.PublisherClient

class EnvVars(NamedTuple):
    gcp_project_id: str
    bq_dataset_name: str
    bq_table_name: str
    topic_ingestion_complete: str