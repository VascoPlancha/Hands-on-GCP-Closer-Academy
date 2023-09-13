import os

import flask
import functions_framework
import joblib
from flask import make_response
from google.cloud import bigquery, storage

try:
    from funcs import gcp_apis, models
except ImportError:
    from d_predictions_endpoint.app.funcs import (
        gcp_apis,
        models,
    )

# Load the pipeline from the pickle file
pipeline = None

################
# 1. Clients ###
################


def load_clients(
    gcp_project_id: str
) -> models.GCPClients:
    """Load the GCP clients.

    Args:
        gcp_project_id (str): The GCP project ID.

    Returns:
        GCPClients: A tuple of GCP clients.
            With the following attributes:
                storage_client: A storage client.
                bigquery_client: A bigquery client.
    """

    storage_client = storage.Client(project=gcp_project_id)
    bigquery_client = bigquery.Client(project=gcp_project_id)

    return models.GCPClients(
        storage_client=storage_client,
        bigquery_client=bigquery_client
    )


def _env_vars() -> models.EnvVars:
    """Load the environment variables.

    This function loads the environment variables required for the application to run. It returns a tuple of environment variables.

    Returns:
        models.EnvVars: A tuple of environment variables.
    """
    # fqn = fully qualified name
    # A table fqn is in the format: project_id.dataset_id.table_id

    return models.EnvVars(
        gcp_project_id=os.getenv("_GCP_PROJECT_ID", 'gcp_project_id'),
        bucket_name=os.getenv("_GCS_BUCKET_NAME_MODELS", 'bucket_name'),
        model_location=os.getenv("_MODEL_LOCATION", 'model_location'),
    )


def load_model(env_vars: models.EnvVars, gcp_clients: models.GCPClients) -> None:
    """
    Downloads a machine learning model from Google Cloud Storage and loads it into memory using joblib.

    Args:
        env_vars (models.EnvVars): An object containing environment variables required for the function.
        gcp_clients (models.GCPClients): An object containing Google Cloud Platform clients required for the function.

    Returns:
        None
    """
    global pipeline
    if pipeline is None:

        # Load the pipeline from the pickle file
        pipeline = joblib.load(
            filename=gcp_apis.transfer_blob_as_bytes(
                CS=gcp_clients.storage_client,
                gcs_input_bucket=env_vars.bucket_name,
                file_location=env_vars.model_location,
            )
        )


if os.getenv("_CI_TESTING", 'no') == 'no':
    env_vars = _env_vars()
    gcp_clients = load_clients(gcp_project_id=env_vars.gcp_project_id)


@functions_framework.http
def predict(request: flask.Request) -> flask.Response:
    if not hasattr(predict, 'env_vars'):
        env_vars = _env_vars()

    if not hasattr(predict, 'gcp_clients'):
        load_clients(
            gcp_project_id=env_vars.gcp_project_id)  # type: ignore
    # # Load the model if it hasn't been loaded yet
    # load_model()

    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        response = make_response('', 204)
        response.headers.set('Access-Control-Allow-Origin', '*')
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.set('Access-Control-Allow-Methods', 'POST')
        return response

    else:
        print(env_vars)  # type: ignore
        return flask.Response(
            response='Hello World!',
            status=200,
            mimetype='text/plain'
        )

    # try:
    #     # Get the input data from the request
    #     if request.content_type != 'application/json':
    #         abort(400, "Content-Type must be 'application/json'")

    #     input_data = json.loads(request.data)

    #     if input_data is None:
    #         abort(400, 'Request must include JSON data')

    #     # Convert the input data to a DataFrame
    #     pd.DataFrame.from_dict([input_data])

    #     # Make a prediction using the pipeline
    #     # prediction = # IMPLEMENTATION [6]: You pipeline object is lodaded globally, just call it and use the `predict` method

    #     # Return the prediction as a JSON response
    #     response = jsonify({'prediction': [prediction.tolist()[0]],
    #                         'uuid': str(uuid.uuid1())})
    #     response.headers.set('Access-Control-Allow-Origin', '*')
    #     return response

    # except:
    #     print(json.dumps({
    #         'severity': "ERROR",
    #         'message': 'Request Failed. traceback: {trace}'.format(trace=traceback.print_exc()),
    #         'request': request.get_json()}
    #     ))
    #     return abort(500, 'Request Failed. traceback: {trace}'.format(trace=traceback.print_exc()))
