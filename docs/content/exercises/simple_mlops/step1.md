# Load a file from Cloud Storage to a Bigquery Table using a Cloud Function

## My tasks

- Mudar o nome do bucket na imagem

## Introduction

![ingestion-architecture](./resources/part_1/ingestion.png)

In this exercise, we will create the `ingest_data` Cloud Function, that will perform the following tasks:

1. The `ingest_data` function will actively monitor the `[YOURNAME]-lz` Google Cloud Storage bucket for new files. This is achieved by configuring a trigger topic (*PubSub*) in the Cloud Function to listen for object creation events in the specified bucket.

2. When a new file is detected, the `ingest_data` function will read the contents of the file and write the data into a BigQuery table named `training_data`. The function will leverage the BigQuery Python client library to facilitate this process, efficiently importing the data from the file into the specified table.

3. After successfully importing the data into BigQuery, the `ingest_data` function will send a message to the `ingestion_complete` topic in Google Cloud Pub/Sub. This message will notify all subscribers that new data has been loaded into BigQuery, allowing them to react accordingly, such as by initiating further data processing tasks.

The Cloud Function `ingest_data` will utilize the Google Cloud Storage, BigQuery, and Pub/Sub client libraries for these tasks. Our goal in this exercise is to develop the code for this function and deploy it to Google Cloud.

The resources needed these tasks are:

- One Bigquery `data set` and one bigquery `table` (The initial schema is available at `./infrastructure/bigquery/titanic_schema.json`)
- One GCS Bucket named `[prefix]-landing-zone-bucket` where you will drop the files once the function is ready
- One GCS Bucket named `[prefix]-functions-bucket` where you will deploy the function source code from.
- One Topic named `[prefix]-ingestion-complete`, to where the function will send a message once complete.

The outline of the *Cloud Function* code is available at `functions/simple_mlops/ingest_data/`.

```text
.
└── ingest_data/
    ├── app/
    │   ├── models.py # Module with models to make typechecking easier. You can safely ignore
    │   ├── gcp_apis.py # Module that contains functions to call google services. Please take a look inside to understand
    │   ├── main.py # The Module you will have to change
    │   └── requirements.txt # Requirements for the function execution
    ├── config/
    │   └── dev.env.yaml # Environment variables that will ship with the function deployment
    └── tests/
        └── test_*.py # Unit tests
```

## Tasks

- [ ] Create a Bigquery Dataset and Table
- [ ] Create a Cloud Storage Bucket
- [ ] Update the Cloud Function Code
- [ ] Deploy the Cloud Function

## Code Changes

Here are the steps necessary to complete the exercise:

1. Create Clients: Use the Google Cloud Storage API, BigQuery API, and PubSub API to create respective client objects.

    ```python
    # INSTRUMENTATION [1]: Use the storage SDK API to make a Client Object
    # INSTRUMENTATION [2]: Use the bigquery SDK API to make a Client Object
    # INSTRUMENTATION [3]: Use the pubsub SDK API to make a PublisherClient Object
    ```

2. Set Environment Variables

    In the `ingest_data/config/dev.env.yaml` file, change the environment variables for the correct ones.

    ```yaml
    _GCP_PROJECT_ID: "The GCP project ID where the resources are located"
    _BIGQUERY_DATASET_ID: "The BigQuery dataset ID you created"
    _BIGQUERY_TABLE_ID: "The BigQuery table ID where you will store the data"
    _TOPIC_INGESTION_COMPLETE: "The Pub/Sub topic ID where you will send a message once the data is ingested"
    ```

3. Send the correct arguments to the `storage_download_blob_as_string` function


1. Insert Rows into BigQuery: Find the correct method to insert rows as JSON into the BigQuery table.
   - Hint: Find all the bigquery `Client()` [methods here](https://cloud.google.com/python/docs/reference/bigquery/latest/google.cloud.bigquery.client.Client)

```python
# IMPLEMENTATION [5]: Find the correct method to use here
```
4 . Publish Message: Find the correct method with the PublisherClient to publish a message.
    - Hint: [PublisherClient](https://cloud.google.com/python/docs/reference/pubsublite/latest/google.cloud.pubsublite.cloudpubsub.publisher_client.PublisherClient#google_cloud_pubsublite_cloudpubsub_publisher_client_PublisherClient_publish)

```python
# IMPLEMENTATION [6]: Find the correct method with the PublisherClient to publish a message
```


5. (Optional) Assign Set Types: You can define a train/test/validation column here. Define that column in your BigQuery table too.

```python
# OPTIONAL [1]: You can define a train / test / validation column here. Define that column in your BigQuery table too.
```

Deployment:

```bash
gcloud functions deploy prefix_ingest_data \
    --region=europe-west3 \
    --runtime=python39 \
    --source=gs://prefix-functions-bucket/ingest_data.zip \
    --entry-point=main \
    --trigger-bucket=prefix-landing-bucket
```

## Documentation

::: simple_mlops.ingest_data.app.main
