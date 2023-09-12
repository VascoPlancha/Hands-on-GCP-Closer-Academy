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

1. Create the client objects: Use the Google Cloud Storage API, BigQuery API, and PubSub API to create respective client objects.

    ```python
    ################
    # 1. Clients ###
    ################
    storage_client = 'Create a storage client here, with the correct project ID argument'
    bigquery_client = 'Create a bigquery client here, with the correct project ID argument'
    publisher = 'Create a publisher client here, with the correct project ID argument'

    return models.GCPClients(
        storage_client=storage_client,
        bigquery_client=bigquery_client,
        publisher=publisher
    )
    ```

2. Set Environment Variables

    In the `ingest_data/config/dev.env.yaml` file, change the environment variables for the correct ones.

    ```python
    ##############################
    # 2. Environment variables ###
    ##############################
    ```

    ```yaml
    _GCP_PROJECT_ID: "The GCP project ID where the resources are located"
    _BIGQUERY_DATASET_ID: "The BigQuery dataset ID you created"
    _BIGQUERY_TABLE_ID: "The BigQuery table ID where you will store the data"
    _TOPIC_INGESTION_COMPLETE: "The Pub/Sub topic ID where you will send a message once the data is ingested"
    ```

3. Send the correct arguments to the `storage_download_blob_as_string` function

    ```python
    #########################################################
    # 3. Correct the arguments below to download the file ###
    #########################################################
    file_contents = gcp_apis.storage_download_blob_as_string(
        CS='??',
        bucket_name='??',
        file_path='??',
    )
    ```

4. Insert Rows into BigQuery: Corrent the arguments in the `bigquery_insert_json_row` function to insert data into the BigQuery table.

    ```python
    ###############################################################
    # 4. Correct the arguments below to insert data into bigquery #
    ###############################################################
    errors = [
        gcp_apis.bigquery_insert_json_row(
            BQ=gcp_clients.bigquery_client,
            table_fqdn=env_vars.bq_table_fqdn,
            row=[datapoint]
        ) for datapoint in transform.titanic_transform(datapoints=datapoints)]

    if any(errors):
        raise ValueError(f"Errors found: {errors}")
    ```

5. Publish Message: Correct the arguments in the `pubsub_publish_message` function, to publish a message.

    ```python
    #########################################################
    # 5. Correct the arguments below to publish a message ###
    #########################################################
    gcp_apis.pubsub_publish_message(
        PS='??',
        project_id='??',
        topic_id='??',
        data=f"I finished ingesting the file {[change me]}!!",
        attributes={'test': 'attribute'},
    )
    ```

6. Deployment

   You can check the deployment here in [Cloud Build](https://console.cloud.google.com/cloud-build/builds;region=europe-west3?referrer=search&project=closeracademy-handson)

    ```bash
    FUNCTION_NAME="ingest_data"
    MY_NAME="MyName"

    gcloud beta functions deploy $MY_NAME-$FUNCTION_NAME \
        --gen2 --cpu=1 --memory=512MB \
        --region=europe-west3 \
        --runtime=python311 \
        --source=functions/simple_mlops/ingest_data/app/ \
        --entry-point=main \
        --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
        --trigger-event-filters="bucket=$MY_NAME-lz"


    gcloud beta functions deploy jm_test_ingest_data \
        --gen2 --cpu=1 --memory=512MB \
        --region=europe-west3 \
        --runtime=python311 \
        --source=functions/simple_mlops/ingest_data/app/ \
        --entry-point=main \
        --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
        --trigger-event-filters="bucket=jm-test-delete-bucket"
    ```

```bash
gcloud functions deploy prefix_ingest_data \
    --region=europe-west3 \
    --runtime=python39 \
    --source=gs://prefix-functions-bucket/ingest_data.zip \
    --entry-point=main \
    --trigger-bucket=prefix-landing-bucket
```

## Hints

### Cloud Events

The CloudEvent argument is an object with the following structure:

```json
{
    "attributes": {
        "specversion": "1.0",
        "id": "1234567890",
        "source": " //pubsub.googleapis.com/projects/[The GCP Project of the topic]/topics/[The topic name]",
        "type": "google.cloud.pubsub.topic.v1.messagePublished",
        "datacontenttype": "application/json",
        "time": "2020-08-08T00:11:44.895529672Z"
    },
    "data": {
        "message": {
            "_comment": "data is base64 encoded string of 'Hello World'",
            "data": "SGVsbG8gV29ybGQ="
        }
    }
}
```

You can read the CloudEvent specification in the [github page](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md).

When a Cloud Storage event is passed to a CloudEvent function, the data payload is of type [StorageObjectData](https://github.com/googleapis/google-cloudevents/blob/main/proto/google/events/cloud/storage/v1/data.proto). This protobuf translates to the following `JSON`:

```json
{
    "attributes": {
        "specversion": "1.0",
        "id": "1234567890",
        "source": "//storage.googleapis.com/projects/_/buckets/[Bucket Name]",
        "type": "google.cloud.storage.object.v1.finalized",
        "datacontenttype": "application/json",
        "time": "2020-08-08T00:11:44.895529672Z"
    },
    "data": {
        "name": "folder/Test.cs [File path inside the bucket]",
        "bucket": "[Bucket Name]",
        "contentType": "application/json",
        "metageneration": "1",
        "timeCreated": "2020-04-23T07:38:57.230Z",
        "updated": "2020-04-23T07:38:57.230Z"
    }
}
```

Read more on how to deploy a function that listens to a Cloud Storage bucket event at:

- [Codelabs - Triggering Event Processing from Cloud Storage using Eventarc and Cloud Functions (2nd gen)](https://codelabs.developers.google.com/triggering-cloud-functions-from-cloud-storage)
- [Cloud Storage Tutorial (2nd gen)](https://cloud.google.com/functions/docs/tutorials/storage)

## Documentation

::: simple_mlops.ingest_data.app.main
