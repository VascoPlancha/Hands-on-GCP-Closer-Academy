
from google.cloud import storage


def transfer_blob_to_temp(
    CS: storage.Client,
    gcs_input_bucket: str,
    file_location: str,
    model_name: str = 'model'
) -> None:
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
        blob.download_to_filename('/tmp/' + model_name)
    else:
        raise ValueError(f'Blob {file_location} does not exist.')
