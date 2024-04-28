import unittest
from a_ingest_data.app.funcs import models


class TestTitanicPassenger(unittest.TestCase):
	def test_to_dict(self):
		passenger = models.TitanicData(
			run_hash='test',
			PassengerId='1',
			Survived='0',
			Pclass='3',
			Name='Braund, Mr. Owen Harris',
			Sex='male',
			Age='22',
			SibSp='1',
			Parch='0',
			Ticket='A/5 21171',
			Fare='7.25',
			Cabin='',
			Embarked='S',
		)

		expected = {
			'run_hash': 'test',
			'PassengerId': '1',
			'Survived': '0',
			'Pclass': '3',
			'Name': 'Braund, Mr. Owen Harris',
			'Sex': 'male',
			'Age': '22',
			'SibSp': '1',
			'Parch': '0',
			'Ticket': 'A/5 21171',
			'Fare': '7.25',
			'Cabin': '',
			'Embarked': 'S',
		}

		self.assertDictEqual(expected, passenger.to_dict())

	def test_to_dict_missing_fields(self):
		"""Test missing fields."""
		passenger = models.TitanicData(
			run_hash='test',
			PassengerId='1',
			Pclass='3',
			Name='Braund, Mr. Owen Harris',
			Sex='male',
		)

		expected = {
			'run_hash': 'test',
			'PassengerId': '1',
			'Pclass': '3',
			'Name': 'Braund, Mr. Owen Harris',
			'Sex': 'male',
			'Age': None,
			'SibSp': None,
			'Parch': None,
			'Ticket': None,
			'Fare': None,
			'Cabin': None,
			'Embarked': None,
		}

		self.assertDictEqual(expected, passenger.to_dict())
