import logging
from os import getenv
from time import sleep
from uuid import uuid4

import docker
import pytest
from confluent_kafka.admin import AdminClient, NewTopic  # noqa
from docker.client import DockerClient
from docker.models.containers import Container
from docker.models.networks import Network
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from mimesis import Field, Schema
from mimesis.locales import Locale

from poc.db.models import get_db_url, Base


# Add helper for data generator
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

logger = logging.getLogger()

KAFKA_IMAGE_NAME = getenv("KAFKA_IMAGE_NAME")
ZOOKEEPER_IMAGE_NAME = getenv("ZOOKEEPER_IMAGE_NAME")
ZOOKEEPER_CLIENT_PORT = getenv("ZOOKEEPER_CLIENT_PORT")
BROKER_PORT = getenv("BROKER_PORT")
LOCAL_PORT = getenv("LOCAL_PORT")

POSTGRES_IMAGE_NAME = getenv("POSTGRES_IMAGE_NAME")
POSTGRES_PORT = getenv("POSTGRES_PORT")
POSTGRES_USER = getenv("POSTGRES_USER")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")
POSTGRES_DB = getenv("POSTGRES_DB")
# PGDATA = getenv("PGDATA")
DB_HOST = getenv("DB_HOST")
DB_URL = getenv("DB_URL")


# def pytest_addoption(parser):
#     parser.addoption("--fixture_scope")


# def determine_scope(fixture_name, config):
#     fixture_scope = config.getoption("--fixture_scope")
#     if fixture_scope is None:
#         fixture_scope = "session"
#     if fixture_scope in [
#         "function",
#         "class",
#         "module",
#         "package",
#         "session",
#     ]:
#         return fixture_scope
#     else:
#         raise ValueError(
#             "Usage: pytest tests/ --fixture_scope=function|class|module|package|session"
#         )


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
def docker_client() -> DockerClient:
    return docker.from_env()


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


@pytest.fixture(scope="session")
def postgres_service_name(resource_postfix: str):
    return f"postgres-{resource_postfix}"


@pytest.fixture(scope="function")
def db_connection(postgres_service_name):
    """SQLAlchemy connection for an empty database.

    Yields:
        _type_: _description_
    """
    # TODO: successfully call get_db_url on network/container
    test_engine = create_engine(DB_URL)
    Base.metadata.create_all(test_engine)
    connection = test_engine.connect()
    yield connection
    connection.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session(postgres_service_name):
    """SQLAlchemy connection for an empty database.

    Yields:
        _type_: _description_
    """
    # TODO: successfully call get_db_url on network/container
    test_engine = create_engine(DB_URL)
    Base.metadata.create_all(test_engine)
    Session = scoped_session(sessionmaker(bind=test_engine))
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)
