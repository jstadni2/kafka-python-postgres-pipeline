from os import getenv
from datetime import datetime

from sqlalchemy import create_engine, URL
from sqlalchemy import Column, Integer, Identity, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base


Base = declarative_base()


def get_db_url(host):
    return URL.create(
        "postgresql+psycopg2",
        username=getenv("POSTGRES_USER"),
        password=getenv("POSTGRES_PASSWORD"),  # plain (unescaped) text
        host=host,
        port=getenv("POSTGRES_PORT"),
        database=getenv("POSTGRES_DB"))


class Person(Base):
    __tablename__ = "person"

    pk = Column(Integer, Identity(start=1), primary_key=True)
    uin = Column(Integer)
    first_name = Column(String())
    middle_name = Column(String())
    last_name = Column(String())
    suffix = Column(String())
    birth_date = Column(DateTime())
    confidential_ind = Column(Boolean())
    gender = Column(String())
    gender_identity_code = Column(String())
    gender_identity_description = Column(String())
    personal_pronoun_code = Column(String())
    personal_pronoun_description = Column(String())
    last_updated = Column(DateTime(), onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"Person(identity_uin={self.uin!r}, " \
               f"first_name={self.first_name!r}, " \
               f"middle_name={self.middle_name!r}), " \
               f"last_name={self.last_name!r}), " \
               f"suffix={self.suffix!r}), "
