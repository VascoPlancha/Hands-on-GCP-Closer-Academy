import deepdiff

from functions.simple_mlops.ingest_data.app import id_transform as transform

# Headers: PassengerId,Survived,Pclass,Name,Sex,Age,SibSp,Parch,Ticket,Fare,Cabin,Embarked
TITANTIC_HEADERS = [
    'PassengerId',
    'Survived',
    'Pclass',
    'Name',
    'Sex',
    'Age',
    'SibSp',
    'Parch',
    'Ticket',
    'Fare',
    'Cabin',
    'Embarked'
]


def test_titanic_transform_line() -> None:
    """Test the first line of the CSV file. A simple line without any quotes."""
    line = '1,0,3,"Braund, Mr. Owen Harris",male,22,1,0,A/5 21171,7.25,,S'

    actual = transform.titanic_transform(
        headers=TITANTIC_HEADERS,
        datapoint=line).to_dict()

    expected = {
        'PassengerId': 1,
        'Survived': False,
        'Pclass': 3,
        'Name': 'Braund, Mr. Owen Harris',
        'Sex': 'male',
        'Age': 22,
        'SibSp': 1,
        'Parch': 0,
        'Ticket': 'A/5 21171',
        'Fare': 7.25,
        'Cabin': '',
        'Embarked': 'S'
    }

    assert {} == deepdiff.DeepDiff(actual, expected)


def test_titanic_line_with_several_quotes() -> None:
    """Test a line of the CSV file with several quotes."""
    line = '23,1,3,"McGowan, Miss. Anna ""Annie""",female,15,0,0,330923,8.0292,,Q'

    actual = transform.titanic_transform(
        headers=TITANTIC_HEADERS,
        datapoint=line).to_dict()

    expected = {
        'PassengerId': 23,
        'Survived': True,
        'Pclass': 3,
        'Name': 'McGowan, Miss. Anna "Annie"',
        'Sex': 'female',
        'Age': 15,
        'SibSp': 0,
        'Parch': 0,
        'Ticket': '330923',
        'Fare': 8.0292,
        'Cabin': '',
        'Embarked': 'Q'
    }

    assert {} == deepdiff.DeepDiff(actual, expected)
