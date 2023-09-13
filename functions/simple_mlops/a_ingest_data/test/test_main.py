from unittest import mock

from functions.simple_mlops.a_ingest_data.app import main

TEST_ENV = {
    '_GCP_PROJECT_ID': 'test-project',
    '_BIGQUERY_DATASET_ID': 'test-dataset',
    '_BIGQUERY_TABLE_ID': 'test-table',
    'TOPIC_INGESTION_COMPLETE': 'test-topic',
}


@mock.patch.dict('os.environ', TEST_ENV)
def test_env_vars() -> None:
    env_vars = main._env_vars()
    print(env_vars)
    assert env_vars.bq_table_fqn == 'test-project.test-dataset.test-table'
