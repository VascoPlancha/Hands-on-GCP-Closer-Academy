"""Models for the ingest_data function. Simplifies"""
from typing import NamedTuple

from google.cloud import bigquery, pubsub, storage


class GCPClients(NamedTuple):
    storage_client: storage.Client
    bigquery_client: bigquery.Client
    publisher: pubsub.PublisherClient


class EnvVars(NamedTuple):
    gcp_project_id: str
    bq_dataset_id: str
    bq_table_id: str
    topic_ingestion_complete: str
