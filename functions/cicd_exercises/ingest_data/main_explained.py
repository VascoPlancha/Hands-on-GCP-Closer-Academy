import random
from typing import Dict, List, Union
from google.cloud import pubsub_v1, bigquery, storage
import json
import csv


def _get_environment_variables():
    """Get environment variables for the project.

    Returns:
        tuple: A tuple containing the project ID, dataset ID, table name, and topic ID.
    """
    project_id: str = "Project_ID"  # Your project ID
    dataset_id: str = "bigquery_dataset_data"
    table_name: str = "bigquery_table_id"
    topic_ingestion_complete = "ingestion-complete"  # The Topic ID you created

    return {
        'project_id': project_id,
        'dataset_id': dataset_id,
        'table_name': table_name,
        'topic_ingestion_complete': topic_ingestion_complete
    }


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
    project_id, dataset_id, table_name, topic_ingestion_complete = _get_environment_variables()

    # Get a reference to the bucket
    bucket = _get_bucket_reference(storage_client, event_data['bucket'])

    # Get a reference to the blob
    blob = _get_blob_reference(bucket, event_data['name'])

    # Read the content of the file
    content = _read_file_content(blob)

    # Split the content by lines
    lines = _split_content_by_lines(content)

    # Get the header (column names) from the first line
    headers = _get_headers(lines)

    # Iterate through the rest of the lines (the data points)
    _process_data_points(
        bigquery_client,
        dataset_id,
        table_name,
        headers,
        lines[1:])

    # Publish the message
    _publish_message(
        publisher, project_id,
        topic_ingestion_complete,
        event_data['name'])


def _get_bucket_reference(
        storage_client: storage.Client,
        bucket_name: str
) -> storage.Bucket:
    """Get a reference to the bucket.

    Args:
        storage_client (storage.Client): The storage client.
        bucket_name (str): The name of the bucket.

    Returns:
        google.cloud.storage.Bucket: A reference to the bucket.
    """
    return storage_client.get_bucket(bucket_name)


def _get_blob_reference(
        bucket: storage.Bucket,
        blob_name: str
) -> storage.Blob:
    """Get a reference to the blob.

    Args:
        bucket (storage.Bucket): The bucket containing the blob.
        blob_name (str): The name of the blob.

    Returns:
        storage.Blob: A reference to the blob.
    """
    return bucket.blob(blob_name)


def _read_file_content(blob: storage.Blob) -> str:
    """Read the content of the file.

    Args:
        blob (storage.Blob): A reference to the blob.

    Returns:
        str: The content of the file.
    """
    with blob.open("r") as f:
        content = f.read()
    return content


def _split_content_by_lines(content: str) -> List[str]:
    """Split the content by lines.

    Args:
        content (str): The content of the file.

    Returns:
        List[str]: A list of lines.
    """
    return content.strip().split('\n')


def _get_headers(lines: List[str]) -> List[str]:
    """Get the headers (column names) from the first line.

    Args:
        lines (List[str]): A list of lines.

    Returns:
        List[str]: A list of headers (column names).
    """
    return lines[0].split(',')


def _process_data_points(
        bigquery_client: bigquery.Client,
        dataset_id: str,
        table_name: str,
        headers: List[str],
        data_points: List[str]) -> None:
    """Process data points and insert them into BigQuery.

    Args:
        bigquery_client (google.cloud.bigquery.Client): The BigQuery client.
        dataset_id (str): The dataset ID.
        table_name (str): The table name.
        headers (List[str]): A list of headers (column names).
        data_points (List[str]): A list of data points as strings.
    """
    for datapoint in data_points:
        # Send all the lines into bigquery the `insert_rows_json` method.
        errors = bigquery_client.insert_rows_json(
            table=f'{dataset_id}.{table_name}',
            json_rows=[_transform_datapoint_into_dictionary(
                headers=headers, datapoint=datapoint)],
        )
        if errors:
            print(json.dumps({
                "message": "Encountered errors while inserting row",
                "errors": errors,
                'data': _transform_datapoint_into_dictionary(headers=headers, datapoint=datapoint),
                "severity": "ERROR",
            }))


def _publish_message(
        publisher: pubsub_v1.PublisherClient,
        project_id: str,
        topic_ingestion_complete: str,
        object_name: str) -> None:
    """Publish a message indicating the completion of the ingestion process.

    Args:
        publisher (PublisherClient): The publisher client.
        project_id (str): The project ID.
        topic_ingestion_complete (str): The topic ID for ingestion completion.
        object_name (str): The name of the ingested object.
    """
    topic_path = publisher.topic_path(project_id, topic_ingestion_complete)
    data = f"I finished ingesting the file {object_name}!!"
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


def _tr_split_datapoint(datapoint: str) -> List[str]:
    """Split a CSV datapoint into values.

    Args:
        datapoint (str): A CSV datapoint as a string.

    Returns:
        List[str]: A list of values from the datapoint.
    """
    return list(csv.reader([datapoint]))[0]


def _tr_validate_datapoint(
        headers: List[str],
        values: List[str]
) -> None:
    """Validate the datapoint by checking if the number of values matches the number of headers.

    Args:
        headers (List[str]): A list of column names for the CSV datapoint.
        values (List[str]): A list of values from the datapoint.

    Raises:
        ValueError: If the number of values in the datapoint does not match the number of headers.
    """
    if len(values) != len(headers):
        raise ValueError(
            "Number of values in datapoint does not match number of headers.")


def _tr_create_data_dict(
        headers: List[str],
        values: List[str]
) -> Dict[str, str]:
    """Create a dictionary from the headers and values using the zip function.

    Args:
        headers (List[str]): A list of column names for the CSV datapoint.
        values (List[str]): A list of values from the datapoint.

    Returns:
        Dict[str, str]: A dictionary representing the datapoint.
    """
    return dict(zip(headers, values))


def _tr_wrangle_data(data_dict: Dict[str, str]) -> Dict[str, Union[str, bool]]:
    """Wrangle the data as necessary.

    Args:
        data_dict (Dict[str, str]): A dictionary representing the datapoint.

    Returns:
        Dict[str, Union[str, bool]]: A dictionary representing the wrangled datapoint.
    """
    data_dict['Survived'] = True if data_dict['Survived'] == '1' else False
    data_dict = {k: v for k, v in data_dict.items() if v or k == 'Survived'}
    return data_dict


def _tr_assign_set_type() -> str:
    """Assign set_type based on a random sample with 70/20/10 split.

    Returns:
        str: The randomly assigned set type ('train', 'test', or 'validation').
    """
    return random.choices(
        ['train', 'test', 'validation'],
        weights=[0.7, 0.2, 0.1],
        k=1)[0]


def _transform_datapoint_into_dictionary(
        headers: List[str],
        datapoint: str
) -> dict:
    """Transforms a CSV datapoint into a dictionary and assigns a set type to the datapoint.

    Args:
        headers (List[str]): A list of column names for the CSV datapoint.
        datapoint (str): A CSV datapoint as a string.

    Returns:
        dict: A dictionary representing the datapoint, with a randomly assigned set type.
              The set type is included as a key-value pair in the dictionary,
              with the key 'set_type'.
    """
    values = _tr_split_datapoint(datapoint)
    _tr_validate_datapoint(headers, values)
    data_dict = _tr_create_data_dict(headers, values)
    data_dict = _tr_wrangle_data(data_dict)
    data_dict['set_type'] = _tr_assign_set_type()

    return data_dict
