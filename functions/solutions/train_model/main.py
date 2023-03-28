import base64
from tempfile import TemporaryFile


from google.cloud import bigquery
from google.cloud import storage
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import joblib


def main(event_data, context) -> None:

    if 'data' in event_data:
        decoded_msg = base64.b64decode(event_data['data']).decode('utf-8')

    storage_client = storage.Client()
    bigquery_client = bigquery.Client()

    def train() -> None:

        # Retrieve data from BigQuery and load it into a pandas DataFrame
        query = """
            SELECT *
            FROM bigquery_dataset_id.table_name
            WHERE set_type = "train"
        """
        df = bigquery_client.query(query).to_dataframe()

        # Preprocess the data
        X = df.drop(columns=['Survived', 'PassengerId',
                    'Name', 'Ticket', 'Cabin', 'set_type'])
        y = df['Survived']

        # Drop rows with missing target values
        missing_target_rows = y.isna()
        X = X[~missing_target_rows]
        y = y[~missing_target_rows]

        # Preprocessing for numerical columns
        numeric_features = ['Age', 'SibSp', 'Parch', 'Fare']
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())])

        # Preprocessing for the 'Sex' column
        sex_feature = ['Sex']
        sex_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='unknown')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))])

        # Preprocessing for the 'Embarked' column
        embarked_feature = ['Embarked']
        embarked_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))])

        # Preprocessing for the 'Pclass' column
        pclass_feature = ['Pclass']
        pclass_transformer = Pipeline(steps=[
            ('onehot', OneHotEncoder(handle_unknown='ignore'))])

        # Combine transformers into a preprocessor
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('sex', sex_transformer, sex_feature),
                ('embarked', embarked_transformer, embarked_feature),
                ('pclass', pclass_transformer, pclass_feature)])

        # Create the pipeline with preprocessing and the Random Forest classifier
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(
                n_estimators=100, random_state=42))
        ])

        # Train the model on the training data
        pipeline.fit(X, y)

        # Save the trained pipeline to a GCS bucket
        bucket_name = 'model-storage-bucket'
        file_name = 'model_titanic.pkl'
        joblib.dump(pipeline, '/tmp/'+file_name)

        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.upload_from_filename('/tmp/'+file_name)

    (train()
     if 'I finished ingesting the file' in decoded_msg
     else print('My Publisher is tricking me.')
     )
