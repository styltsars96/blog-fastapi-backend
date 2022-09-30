"""
Database configuration utility.
"""
from os import environ, path
from dotenv import load_dotenv
from sqlalchemy_utils import create_database, database_exists

load_dotenv(path.dirname(path.realpath(__file__)) + "/../.env")

DATABASE_USER = environ.get("DATABASE_USER", "user")
DATABASE_PASSWORD = environ.get("DATABASE_PASSWORD", "password")
DATABASE_HOST = environ.get("DATABASE_HOST", "localhost")

TESTING = environ.get("TESTING")

if TESTING:
    # Use separate DB for tests
    DATABASE_NAME = "blogs-temp-for-test"
    TEST_SQLALCHEMY_DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:5432/{DATABASE_NAME}"
    DATABASE_URL = TEST_SQLALCHEMY_DATABASE_URL
else:
    DATABASE_NAME = environ.get("PROJECT_NAME", "blogs")
    SQLALCHEMY_DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:5432/{DATABASE_NAME}"
    DATABASE_URL = SQLALCHEMY_DATABASE_URL

# Set it up for universal use in the current process
environ["DATABASE_URL"] = DATABASE_URL


def validate_database():
    """validate_database
    Creates the database if it does not exist
    """
    if not database_exists(DATABASE_URL):
        create_database(DATABASE_URL)
