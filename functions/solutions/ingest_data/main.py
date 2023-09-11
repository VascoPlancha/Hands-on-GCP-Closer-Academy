import random
from typing import List
from google.cloud import pubsub_v1, bigquery, storage
import json
import csv


def main(event_data, context):
    """Entrypoint of the cloud function

    Args:
        event_data (dict): Event payload
        context (dict): Event context.
    """
    # Clients
    storage_client = storage.Client()
    bigquery_client = bigquery.Client()
    publisher = pubsub_v1.PublisherClient()

    # Environment variables
    # Note: In a real environment these variables would be passed by environment variables.
    # See: https://cloud.google.com/sdk/gcloud/reference/functions/deploy#--env-vars-file
    project_id: str = "Project_ID"  # Your project ID
    dataset_id: str = "bigquery_dataset_data"
    table_name: str = "bigquery_table_id"
    topic_ingestion_complete = "ingestion-complete"  # The Topic ID you created

    # Get a reference to the bucket
    bucket: storage.Bucket = storage_client.get_bucket(event_data['bucket'])
    # The key 'bucket' exists in the event_data

    # The ID of your new GCS object
    # blob_name = "storage-object-name"
    blob: storage.Blob = bucket.blob(event_data['name'])

    # Iterate over the file
    with blob.open("r") as f:  # Link [1]
        # Read the entire content of the file
        content: str = f.read()

    # Split the content by lines
    lines: List[str] = content.strip().split('\n')

    # Get the header (column names) from the first line
    headers: List[str] = lines[0].split(',')

    # Iterate through the rest of the lines (the data points)
    for datapoint in lines[1:]:
        # Send all the lines into bigquery the `insert_rows_json` method.
        errors = bigquery_client.insert_rows_json(
            table=f'{dataset_id}.{table_name}',
            json_rows=[_transform_datapoint_into_dictionary(
                headers=headers,
                datapoint=datapoint)],
        )
        if errors:
            print(json.dumps({
                "message": "Encountered errors while inserting row",
                "errors": errors,
                'data': _transform_datapoint_into_dictionary(
                    headers=headers,
                    datapoint=datapoint),
                "severity": "ERROR",
            }))

    # Publish the message
    # Define the topic path, it's a string "projects/[PROJECT_ID]/topics/[TOPIC_ID]"
    # but the `topic_path` method helps us.
    topic_path: str = publisher.topic_path(
        project_id, topic_ingestion_complete)
    data = f"I finished ingesting the file {event_data['name']}!!"

    # When you publish a message, the client returns a future.
    # You don't have to wait for it, you can alternatively write:
    # _ = publisher.publish(topic_path, data.encode("utf-8"))
    # or just
    # publisher.publish(topic_path, data.encode("utf-8"))
    publish_future = publisher.publish(topic_path, data.encode("utf-8"))


def _transform_datapoint_into_dictionary(headers: List[str], datapoint: str) -> dict:
    """Transforms a CSV datapoint into a dictionary and assigns a 
        set type to the datapoint.

    Args:
        headers (List[str]): A list of column names for the CSV datapoint.
        datapoint (str): A CSV datapoint as a string.

    Returns:
        dict: A dictionary representing the datapoint, with a randomly assigned set type.
              The set type is included as a key-value pair in the dictionary, 
              with the key 'set_type'.

    Raises:
        ValueError: If the number of values in the datapoint does not match the number of headers.

    """
    # Split the datapoint into values
    values = list(csv.reader([datapoint]))[0]

    # Check that the number of values matches the number of headers
    if len(values) != len(headers):
        raise ValueError(
            "Number of values in datapoint does not match number of headers.")

    # Create a dictionary from the headers and values using the zip function
    data_dict = dict(zip(headers, values))

    # Wrangle the data as necessary
    data_dict['Survived'] = True if data_dict['Survived'] == '1' else False
    data_dict = {k: v for k, v in data_dict.items() if v or k == 'Survived'}

    # Assign set_type based on a random sample with 70/20/10 split
    set_type = random.choices(
        ['train', 'test', 'validation'],
        weights=[0.7, 0.2, 0.1],
        k=1)[0]

    data_dict['set_type'] = set_type

    return data_dict
