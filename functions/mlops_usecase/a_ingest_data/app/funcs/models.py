"""Models for the ingest_data function. Simplifies type hinting."""

from dataclasses import dataclass
from typing import Any, Dict, NamedTuple

from google.cloud import bigquery, pubsub, storage


class GCPClients(NamedTuple):
	"""A named tuple that contains GCP client objects for Storage, BigQuery, and Pub/Sub.

	Attributes:
	    storage_client (google.cloud.storage.Client): A client object for Google Cloud Storage.
	    bigquery_client (google.cloud.bigquery.Client): A client object for Google BigQuery.
	    publisher (google.cloud.pubsub_v1.PublisherClient): A client object for Google Cloud Pub/Sub.
	"""

	storage_client: storage.Client
	bigquery_client: bigquery.Client
	publisher: pubsub.PublisherClient


class EnvVars(NamedTuple):
	"""A named tuple representing environment variables required for data ingestion.

	Attributes:
	    gcp_project_id (str): The ID of the Google Cloud Platform project.
	    bq_table_fqn (str): The fully-qualified name of the BigQuery table.
	    topic_ingestion_complete (str): The name of the Pub/Sub topic for ingestion completion notifications.
	"""

	gcp_project_id: str
	bq_table_fqn: str
	topic_ingestion_complete: str


@dataclass(kw_only=True, frozen=True)
class TitanicData:
	"""A class representing the data for the titanic dataset.

	Attributes:
		run_hash (str): The hash of the run.
		PassengerId (Optional[str]): The ID of the passenger.
		Survived (Optional[str]): Whether the passenger survived or not.
		Pclass (Optional[str]): The class of the passenger's ticket.
		Name (Optional[str]): The name of the passenger.
		Sex (Optional[str]): The gender of the passenger.
		Age (Optional[str]): The age of the passenger.
		SibSp (Optional[str]): The number of siblings/spouses aboard the Titanic.
		Parch (Optional[str]): The number of parents/children aboard the Titanic.
		Ticket (Optional[str]): The ticket number of the passenger.
		Fare (Optional[str]): The fare paid by the passenger.
		Cabin (Optional[str]): The cabin number of the passenger.
		Embarked (Optional[str]): The port of embarkation of the passenger.
	"""

	run_hash: str
	PassengerId: str | None
	Survived: str | None = None
	Pclass: str | None = None
	Name: str | None
	Sex: str | None = None
	Age: str | None = None
	SibSp: str | None = None
	Parch: str | None = None
	Ticket: str | None = None
	Fare: str | None = None
	Cabin: str | None = None
	Embarked: str | None = None

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> 'TitanicData':
		"""Creates a new instance of the TitanicData class from a dictionary.

		Args:
		    data (Dict[str, Any]): A dictionary containing the data for a single passenger.

		Returns:
		    TitanicData: A new instance of the TitanicData class.
		"""
		# Convert the Survived column to a boolean
		return cls(**data)

	def to_dict(self) -> Dict[str, Any]:
		"""Converts the TitanicData instance to a dictionary.

		Returns:
		    Dict[str, Any]: A dictionary containing the data for a single passenger.
		"""
		return {
			'run_hash': self.run_hash,
			'PassengerId': self.PassengerId,
			'Survived': self.Survived,
			'Pclass': self.Pclass,
			'Name': self.Name,
			'Sex': self.Sex,
			'Age': self.Age,
			'SibSp': self.SibSp,
			'Parch': self.Parch,
			'Ticket': self.Ticket,
			'Fare': self.Fare,
			'Cabin': self.Cabin,
			'Embarked': self.Embarked,
		}
