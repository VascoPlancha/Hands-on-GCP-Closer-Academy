
from google.cloud import storage


def transfer_blob_as_bytes(
    CS: storage.Client,
    gcs_input_bucket: str,
    file_location: str,
) -> bytes:
    """
    Downloads a blob from a Google Cloud Storage bucket as bytes.

    Args:
        CS (storage.Client): A Google Cloud Storage client object.
        gcs_input_bucket (str): The name of the Google Cloud Storage bucket.
        file_location (str): The location of the blob in the bucket.

    Returns:
        bytes: The contents of the blob as bytes.

    Raises:
        ValueError: If the specified blob does not exist in the bucket.
    """

    # Getting the bucket
    bucket = CS.bucket(gcs_input_bucket)

    # Getting the blob
    blob = bucket.blob(file_location)

    if blob.exists():
        # Downloading the blob
        return blob.download_as_bytes()
    else:
        raise ValueError(f'Blob {file_location} does not exist.')
