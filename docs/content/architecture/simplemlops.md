# Architecure

We are going to build a simple *MLOps* project in *Google Cloud Platform* using
`Cloud Storage`, `Cloud Functions`, `Bigquery` and `Pubsub`.

Our minimal *MLOps* system should look like this in the end:

![architecture](../resources/architecture/architecture.png)

## Ingestion and training

1. Cloud Function `ingest_data` monitors the `my-data-landing-zone` for new files.
2. Upon detecting a new file, `ingest_data` writes its contents to the BigQuery table `training_data`.
3. A message is sent to the `ingestion_complete` topic, notifying subscribers about the new data in BigQuery.
4. The `train_model` Cloud Function, subscribed to `ingestion_complete`, is triggered and begins training.
5. It retrieves data from the `training_data` BigQuery table.
6. The trained model is saved in the `my-model-storage` bucket.

### Make the model available

11. The `predictions_endpoint` Cloud Function receives a request containing new data from a client.
12. The Function loads the previously stored model into memory.
13. It makes a prediction and stores the prediction and new data in the `predictions_data` BigQuery table.
14. The prediction result is returned to the client.