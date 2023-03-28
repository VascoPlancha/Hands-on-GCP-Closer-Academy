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

    The --trigger-bucket event_data is the following:
    https://github.com/googleapis/google-cloudevents/blob/main/proto/google/events/cloud/storage/v1/data.proto

    ```json
    event_data: {
        storageClass: string
        size: string
        id: string
        selfLink: string
        timeStorageClassUpdated: Timestamp
        updated: Timestamp
        crc32c: string
        generation: string
        timeCreated: Timestamp
        mediaLink: string
        etag: string
        name: string
        bucket: string
        md5Hash: string
        metageneration: string
        contentType: string
        kind: string
    }
    ```

    The important keys to us now are `name`, which is the name of the file
    that triggered the event, and `bucket`, which is the bucket this
    cloud function is listening.
    """
    # Clients
    # storage_client = # IMPLEMENTATION [1]: Use the storage API to make a Client Object
    # bigquery_client = # IMPLEMENTATION [2]: Use the bigquery API to make a Client Object
    # publisher = # IMPLEMENTATION [3]: Use the pubsub_b1 API to make a PubliserClient Object

    # Environment variables
    # Note: In a real environment these variables would be passed by environment variables.
    # See: https://cloud.google.com/sdk/gcloud/reference/functions/deploy#--env-vars-file
    project_id: str = "Your project ID" # IMPLEMENTATION [4]: Set your configurations here
    dataset_id: str = "Your Data set ID" # IMPLEMENTATION [4]: Set your configurations here
    table_name: str = "Your Table ID" # IMPLEMENTATION [4]: Set your configurations here
    topic_ingestion_complete = "Your Topic ID" # IMPLEMENTATION [4]: Set your configurations here

    # Get a reference to the bucket
    bucket: storage.Bucket = storage_client.get_bucket(event_data['bucket'])
    # The key 'bucket' exists in the event_data

    # The ID of your new GCS object
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
        errors = bigquery_client._( # IMPLEMENTATION [5]: Find the correct method to use here
            table=f"{dataset_id}.",
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

    # Publish the message
    # publish_future = # IMPLEMENTATION [6]: Find the correct method with the PublisherClient to publish a message


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
    # OPTIONAL [1]: You can define a train / test / validation column here. Define that column in your bigquery table too.

    return data_dict
