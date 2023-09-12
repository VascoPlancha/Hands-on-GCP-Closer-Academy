import csv
from typing import Generator, List

from . import models


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
    datapoints: List[str],
) -> Generator[models.TitanicData, None, None]:
    """Generator that transforms a CSV datapoint into a titanic data object.

    Args:
        headers (List[str]): The headers of the CSV file.
        datapoint (str): A CSV datapoint as a string.

    Yields:
        models.TitanicData: A titanic data object.
    """
    for datapoint in datapoints:
        datapoint_decoded = list(csv.reader([datapoint]))[0]

        # Zip the headers and values together into a dictionary
        datapoint_obj = models.TitanicData(
            PassengerId=int(datapoint_decoded[0]),
            Survived=True if datapoint_decoded[1] == '1' else False,
            Pclass=int(datapoint_decoded[2]),
            Name=datapoint_decoded[3],
            Sex=datapoint_decoded[4],
            Age=int(datapoint_decoded[5]),
            SibSp=int(datapoint_decoded[6]),
            Parch=int(datapoint_decoded[7]),
            Ticket=datapoint_decoded[8],
            Fare=float(datapoint_decoded[9]),
            Cabin=datapoint_decoded[10],
            Embarked=datapoint_decoded[11],
        )

        # Yield the datapoint object
        yield datapoint_obj
