import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Pull variables directly from environment (assumes they are already set)
DATABASE_USER = os.environ["DATABASE_USER"]
DATABASE_PASSWORD = os.environ["DATABASE_PASSWORD"]
DATABASE_HOST = os.environ["DATABASE_HOST"]
DATABASE_PORT = os.environ["DATABASE_PORT"]
DATABASE_NAME = os.environ["DATABASE_NAME"]

# assert if each of the variables are not none
assert DATABASE_USER is not None, "DATABASE_USER is not set"
assert DATABASE_PASSWORD is not None, "DATABASE_PASSWORD is not set"
assert DATABASE_HOST is not None, "DATABASE_HOST is not set"
assert DATABASE_PORT is not None, "DATABASE_PORT is not set"
assert DATABASE_NAME is not None, "DATABASE_NAME is not set"

# Construct the database URL
DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# Create engine and session factory
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
