import logging
from os import getenv
from time import sleep
from uuid import uuid4

import pytest
from confluent_kafka.admin import AdminClient, NewTopic  # noqa
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from mimesis import Field, Schema
from mimesis.locales import Locale

from poc.db.models import get_db_url, Base


LOCAL_PORT = getenv("LOCAL_PORT")
DB_HOST = getenv("DB_HOST")

logger = logging.getLogger()

class DataGenerator:
    @staticmethod
    def person(count):
        field = Field(locale=Locale.EN)
        # TODO: generate gender and personal pronounces
        schema = Schema(
            schema=lambda: {
                'uin': field('numeric.integer_number', start=111111111, end=199999999),
                'first_name': field('first_name'),
                'middle_name': field('first_name'),
                'last_name': field('person.last_name'),
                'birth_date': field('datetime.formatted_date', start=1950, end=2003),
                'confidential_ind': field('development.boolean'),
            },
            iterations=count
        )
        return schema.create()


@pytest.fixture
def data_generator():
    return DataGenerator


@pytest.fixture(scope="session")
def resource_postfix() -> str:
    return str(uuid4()).partition("-")[0]


@pytest.fixture(scope="session")
def topic_name(resource_postfix: str) -> str:
    return f"demo-topic-{resource_postfix}"


@pytest.fixture(scope="session")
def consumer_id(resource_postfix: str) -> str:
    return f"demo-consumer-{resource_postfix}"


@pytest.fixture(scope="session")
def kafka_admin_client() -> AdminClient:
    admin_client = AdminClient(conf={"bootstrap.servers": f"0.0.0.0:{LOCAL_PORT}"})
    return admin_client


@pytest.fixture(scope="session")
def new_topic(kafka_admin_client: AdminClient, topic_name: str) -> NewTopic:
    new_topic = NewTopic(
        topic=topic_name,
        num_partitions=1,
        replication_factor=1,
    )
    kafka_admin_client.create_topics(new_topics=[new_topic])
    topic_exists = False
    while not topic_exists:
        logging.info(f"Waiting for topic {new_topic.topic} to be created")
        sleep(1)
        cluster_metadata = kafka_admin_client.list_topics()
        topics = cluster_metadata.topics
        topic_exists = new_topic.topic in topics.keys()
    yield new_topic
    kafka_admin_client.delete_topics(topics=[new_topic.topic])


@pytest.fixture(scope="function")
def db_connection():
    """SQLAlchemy connection for an empty database.

    Yields:
        _type_: _description_
    """
    test_engine = create_engine(get_db_url(DB_HOST))
    Base.metadata.create_all(test_engine)
    connection = test_engine.connect()
    yield connection
    connection.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """SQLAlchemy session for an empty database.

    Yields:
        _type_: _description_
    """
    test_engine = create_engine(get_db_url(DB_HOST))
    Base.metadata.create_all(test_engine)
    Session = scoped_session(sessionmaker(bind=test_engine))
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)
