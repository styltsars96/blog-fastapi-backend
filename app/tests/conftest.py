"""
Pytest configuration / setup
"""
import os

import pytest

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from sqlalchemy_utils import create_database, drop_database

# If placed below the application import, it would raise an error:
# 'TESTING' has already been read from the environment (due to database module).
os.environ["TESTING"] = "True"
# pylint: disable=wrong-import-position
from app import database


@pytest.fixture(scope="module")
def temp_db():
    """
    Create new DB for tests only.
    Drop this DB once all tests are done.
    """
    create_database(database.TEST_SQLALCHEMY_DATABASE_URL)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    alembic_cfg = AlembicConfig(os.path.join(base_dir, "alembic.ini"))
    alembic_command.upgrade(alembic_cfg, "head")

    try:
        yield database.TEST_SQLALCHEMY_DATABASE_URL
    finally:
        drop_database(database.TEST_SQLALCHEMY_DATABASE_URL)
