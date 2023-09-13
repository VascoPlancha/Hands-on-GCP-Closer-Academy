"""Common functions for the update_facts pipeline."""
from pathlib import Path


def file_contents(path: Path) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().replace('\n', ' ')


from pathlib import Path


def query_train_data(
    table_fqn: str,
    query_path: Path,
) -> str:
    '''Query to get training data from BigQuery.

    This function uses the function file_contents to call the appropriate
    SQL query and formats it with this function parameters.

    Args:
        table_fqn (str): The fully-qualified name of the table in BigQuery.
        query_path (Path): The path to the SQL query script.

    Returns:
        str: A string with the query built based on the args.
        This query can be executed later.
    '''
    query: str = file_contents(
        path=query_path
    ).format(
        table_source=table_fqn,
    )
    return query
