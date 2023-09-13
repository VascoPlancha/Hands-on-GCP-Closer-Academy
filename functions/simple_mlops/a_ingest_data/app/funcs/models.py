"""Models for the ingest_data function. Simplifies type hinting."""
from dataclasses import dataclass
from typing import Any, Dict, NamedTuple

from google.cloud import bigquery, pubsub, storage


class GCPClients(NamedTuple):
    storage_client: storage.Client
    bigquery_client: bigquery.Client
    publisher: pubsub.PublisherClient


class EnvVars(NamedTuple):
    gcp_project_id: str
    bq_table_fqdn: str
    topic_ingestion_complete: str


@dataclass(kw_only=True, frozen=True)
class TitanicData():
    """The data for the titanic dataset."""
    PassengerId: str | None
    Survived: str | None
    Pclass: str | None
    Name: str | None
    Sex: str | None
    Age: str | None
    SibSp: str | None
    Parch: str | None
    Ticket: str | None
    Fare: str | None
    Cabin: str | None
    Embarked: str | None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TitanicData':
        # Convert the Survived column to a boolean
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return {
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
            'Embarked': self.Embarked
        }
