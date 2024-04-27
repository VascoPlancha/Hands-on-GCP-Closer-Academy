"""Cloud Function to Ingest Data."""

import os

import functions_framework
from cloudevents.http import CloudEvent
from google.cloud import bigquery, pubsub, storage

try:
	from funcs import gcp_apis, models, transform
except ImportError:
	from a_ingest_data.app.funcs import (
		gcp_apis,
		models,
		transform,
	)

##############################################
# 0. Create the necessary resources in GCP ###
##############################################

################
# 1. Clients ###
################


def load_clients(gcp_project_id: str) -> models.GCPClients:
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

	return models.GCPClients(storage_client=storage_client, bigquery_client=bigquery_client, publisher=publisher)


##############################
# 2. Environment variables ###
##############################


def _env_vars() -> models.EnvVars:
	"""Return an instance of the EnvVars class.

	Attributes:
	    gcp_project_id: The ID of the GCP project.
	    bq_table_fqn: The fully qualified name of the BigQuery table in the format:
	                 project_id.dataset_id.table_id.
	    topic_ingestion_complete: The name of the Pub/Sub topic to publish a message
	    to when data ingestion is complete.

	Returns:
	    models.EnvVars: The env vars.
	"""
	# fqn = fully qualified name
	# A table fqn is in the format: project_id.dataset_id.table_id

	return models.EnvVars(
		gcp_project_id=os.getenv('_GCP_PROJECT_ID', 'gcp_project_id'),
		bq_table_fqn=f"""{os.getenv("_GCP_PROJECT_ID", "gcp_project_id")}.\
{os.getenv("_BIGQUERY_DATASET_ID", "bq_table_fqn_dst")}.\
{os.getenv("_BIGQUERY_TABLE_ID", "bq_table_fqn_tbl")}""",
		topic_ingestion_complete=os.getenv('_TOPIC_INGESTION_COMPLETE', 'topic_ingestion_complete'),
	)


if os.getenv('_CI_TESTING', 'no') == 'no':
	env_vars = _env_vars()
	gcp_clients = load_clients(gcp_project_id=env_vars.gcp_project_id)


@functions_framework.cloud_event
def main(cloud_event: CloudEvent) -> None:
	"""Entrypoint of the cloud function.

	Args:
	    cloud_event (CloudEvent): The cloud event that triggered this function.
	"""
	print(cloud_event)
	if not hasattr(main, 'env_vars'):
		env_vars = _env_vars()

	if not hasattr(main, 'gcp_clients'):
		gcp_clients = load_clients(gcp_project_id=env_vars.gcp_project_id)  # type: ignore

	# Get the data from the cloud event
	data: dict = cloud_event.get_data()  # type: ignore

	file_contents = gcp_apis.storage_download_blob_as_string(
		CS=gcp_clients.storage_client,  # type: ignore
		bucket_name=data['bucket'],
		file_path=data['name'],
	)

	# Split the content by lines
	datapoints = transform.split_lines(content=file_contents)

	# Get the headers (column names) from the first line
	has_headers = True
	if has_headers:
		datapoints = datapoints[1:]

	# Iterate through the the datapoints and insert them into BigQuery
	errors = [
		gcp_apis.bigquery_insert_json_row(
			BQ=gcp_clients.bigquery_client,  # type: ignore
			table_fqn=env_vars.bq_table_fqn,  # type: ignore
			row=[datapoint.to_dict()],
		)
		for datapoint in transform.titanic_transform(datapoints=datapoints)
	]

	if any(errors):
		raise ValueError(f'Errors found: {errors}')

	gcp_apis.pubsub_publish_message(
		PS=gcp_clients.publisher,  # type: ignore
		project_id=env_vars.gcp_project_id,  # type: ignore
		topic_id=env_vars.topic_ingestion_complete,  # type: ignore
		message=f"I finished ingesting the file {data['name']}!!",
		attributes={},
	)
