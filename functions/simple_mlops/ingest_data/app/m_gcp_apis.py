"""This module contains the functions that interact with the GCP APIs."""
from google.cloud import storage


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
