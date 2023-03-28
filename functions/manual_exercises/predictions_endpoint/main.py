import joblib
import pandas as pd
from flask import abort, jsonify, make_response
from google.cloud import storage
import uuid
import traceback
import json

# Load the pipeline from the pickle file
pipeline = None


def load_model():
    global pipeline
    if pipeline is None:
        # Download the model from GCS
        # bucket_name = # IMPLEMENTATION [1]: Add your prefix-bucket-models here
        # file_name = # IMPLEMENTATION [2]: Put the name you gave your model here
        # storage_client = # IMPLEMENTATION [3]: Use the storage API to make a Client Object
        # bucket = # IMPLEMENTATION [4]: Connect to the bucket in [4] using the correct method for the storage Client.
        # blob = # IMPLEMENTATION [5]: Connect to the blob(file object) inside the bucket, using the `bucket` object.
        blob.download_to_filename('/tmp/' + file_name)

        # Load the pipeline from the pickle file
        pipeline = joblib.load('/tmp/' + file_name)


def predict(request):
    # Load the model if it hasn't been loaded yet
    load_model()

    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        response = make_response('', 204)
        response.headers.set('Access-Control-Allow-Origin', '*')
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.set('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        # Get the input data from the request
        if request.content_type != 'application/json':
            abort(400, "Content-Type must be 'application/json'")

        input_data = json.loads(request.data)

        if input_data is None:
            abort(400, 'Request must include JSON data')

        # Convert the input data to a DataFrame
        input_df = pd.DataFrame.from_dict([input_data])

        # Make a prediction using the pipeline
        # prediction = # IMPLEMENTATION [6]: You pipeline object is lodaded globally, just call it and use the `predict` method

        # Return the prediction as a JSON response
        response = jsonify({'prediction': [prediction.tolist()[0]],
                            'uuid': str(uuid.uuid1())})
        response.headers.set('Access-Control-Allow-Origin', '*')
        return response

    except:
        print(json.dumps({
            'severity': "ERROR",
            'message': 'Request Failed. traceback: {trace}'.format(trace=traceback.print_exc()),
            'request': request.get_json()}
        ))
