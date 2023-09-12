"""This module contains the functions that interact with the GCP APIs."""
from typing import Any, Dict

from google.cloud import bigquery, pubsub, storage


def storage_download_blob_as_string(
    CS: storage.Client,
    bucket_name: str,
    file_path: str,
) -> str:
    """Transfers the result to a local folder.

    Args:
        bucket_name (str): The name of the bucket.
        file_path (str): The location of the blob/file inside the bucket.

    Returns:
        str: A string with the file content.

    Raises:
        ValueError: If the blob does not exist.
    """
    # Getting the bucket
    bucket = CS.bucket(bucket_name)

    # Getting the blob
    blob = bucket.blob(file_path)

    if blob.exists():
        # Downloading the blob
        return blob.download_as_text()
    else:
        raise ValueError(f'Blob {file_path} does not exist.')


def bigquery_insert_json_row(
    BQ: bigquery.Client,
    table_fqdn: str,
    row: Dict[str, Any],
) -> Any:
    """Inserts a row into a bigquery table.

    Args:
        BQ (bigquery.Client): The bigquery client.
        table_fqdn (str): The fully qualified name of the table.
        row (Dict[str, Any]): The row to insert into the table.
    """
    errors = BQ.insert_rows_json(
        table=table_fqdn,
        json_rows=[row],
    )

    if errors:
        return errors
    else:
        return None


def pubsub_publish_message(
    PS: pubsub.PublisherClient,
    project_id: str,
    topic_id: str,
    message: str,
    attributes: Dict[str, str] = {},
) -> None:
    """Publishes a message to a Pub/Sub topic.

    Args:
        PS (pubsub.PublisherClient): The pubsub client.
        project_id (str): The ID of the project where the topic is located.
        topic_id (str): The ID of the topic.
        message (str): The message to publish.
        attributes (Dict[str, str], optional): The attributes of the message.
            Defaults to {}.
    """
    _topic = PS.topic_path(project_id, topic_id)

    PS.publish(
        topic=_topic,
        data=message.encode('utf-8'),
        **attributes,)
