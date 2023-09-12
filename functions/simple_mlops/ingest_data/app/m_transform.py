from typing import Dict, List


def split_lines(
    content: str,
) -> List[str]:
    """Split the content by lines.

    Args:
        content (str): The content of the file.

    Returns:
        List[str]: The lines of the file.
    """
    return content.strip().split('\n')


def titanic_transform(
    line: str,
) -> Dict[str, str]:
    """Transform the titanic data into a dictionary of rows.

    Args:
        content (str): The content of the file.

    Returns:
        Dict[str, str]:
    """
    return {'one': 'two'}
