from typing import Any

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def main(event_data: dict, context: Any) -> None:

    if 'data' in event_data:
        # decoded_msg = # IMPLEMENTATION [1]: Add code to decode the base64 message.
        pass  # Remove pass once above line is done

    # storage_client = # IMPLEMENTATION [1]: Use the storage API to make a Client Object
    # bigquery_client = # IMPLEMENTATION [2]: Use the bigquery API to make a Client Object

    def train() -> None:

        # Retrieve data from BigQuery and load it into a pandas DataFrame
        # IMPLEMENTATION [3]: Create an SQL query to retrieve data from the bigquery table with titanic data.
        query = ""

        df = bigquery_client.query(query).to_dataframe()

        # Preprocess the data
        X = df.drop(columns=['Survived', 'PassengerId',
                    'Name', 'Ticket', 'Cabin'])  # OPTIONAL [1]: add 'set_type' or other columns that shouldn't be passed to the model.
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
        # bucket_name = 'Your Bucket Name' # IMPLEMENTATION [4]: Add your prefix-bucket-models here
        # file_name = 'your_model_name.pkl' # IMPLEMENTATION [5]: Give a name to your model.
        joblib.dump(pipeline, '/tmp/'+file_name)

        # bucket = # IMPLEMENTATION [6]: Connect to the bucket in [4] using the correct method for the storage Client.
        # blob = # IMPLEMENTATION [7]: Connect to the blob(file object) inside the bucket, using the `bucket` object.
        blob.upload_from_filename('/tmp/'+file_name)

    (train()
     if 'I finished ingesting the file' in decoded_msg
     else print('My Publisher is tricking me.')
     )
