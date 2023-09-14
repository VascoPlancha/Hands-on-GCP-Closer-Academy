# 3. Create an endpoint to serve the model to the outside world

![img-prediction-architecture](./resources/part_4/predictions.png)

In this exercise, you'll be working with the `predictions_endpoint` Cloud Function. This HTTP-triggered function serves as the prediction endpoint for clients to send new data points. Upon receiving a request containing new data, the function performs the following steps:

1. It loads the previously trained model from the `my-model-storage` bucket into memory.
2. Utilizing the loaded model, it generates a prediction based on the new data point received in the request.
3. The function then stores both the prediction and the new data in the `predictions_data` BigQuery table to maintain a record of all predictions.
4. Finally, it returns the prediction result to the client, completing the request-response cycle.

Your task is to develop the code for the `predictions_endpoint` Cloud Function and deploy it, ensuring that it can efficiently handle the entire process from receiving new data to returning predictions.

The outline of the *Cloud Function* code is available at `./functions/manual_exercises/train_model/`

1. Set Bucket Name: Add the GCS bucket name where your model is stored.

```python
# IMPLEMENTATION [1]: Add your prefix-bucket-models here
```

2. Set Model Filename: Provide the name you gave to your model.

```python
# IMPLEMENTATION [2]: Put the name you gave your model here
```

3. Create Storage Client: Use the storage API to make a Client Object.

```python
# IMPLEMENTATION [3]: Use the storage API to make a Client Object
```

4. Connect to Bucket: Connect to the GCS bucket using the correct method for the Storage Client.

```python
# IMPLEMENTATION [4]: Connect to the bucket in [4] using the correct method for the storage Client.
```

5. Connect to Blob: Connect to the blob (file object) inside the bucket, using the bucket object.

```python
# IMPLEMENTATION [5]: Connect to the blob(file object) inside the bucket, using the `bucket` object.
```

6. Make Prediction: Call the predict method of the global pipeline object to make a prediction.

```python
# IMPLEMENTATION [6]: You pipeline object is lodaded globally, just call it and use the `predict` method
```

Deployment:

```bash
gcloud beta functions deploy jm_test-predictions_endpoint \
    --gen2 --cpu=1 --memory=1024MB \
    --region=europe-west3 \
    --runtime=python311 \
    --source=functions/simple_mlops/d_predictions_endpoint/app/ \
    --env-vars-file=functions/simple_mlops/d_predictions_endpoint/config/dev.env.yaml \
    --entry-point=predict \
    --trigger-http \
    --allow-unauthenticated
```

You can make requests with a cURL comamnd like so:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"Pclass": 3, "Name": "Some Name", "Sex": "male", "Age": 22, "SibSp": 1, "Parch": 0, "Ticket": "A/5 21171", "Fare": 7.25, "Cabin": "", "Embarked": "S"}' http://YOUR_FUNCTION_ENDPOINT
```

or by going to the app [on Stackblitz](https://stackblitz.com/edit/closer-gcp-titanic-frontend-example?file=src%2Fapp%2Ftitanic-prediction.service.ts) and change the `TitanicEndpoint` variable in `./src/app/titanic-prediction.service.ts`.

## Code

Remember, you can still find it in the correct folder.

::: simple_mlops.d_predictions_endpoint.app.main
