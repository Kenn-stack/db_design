import pytest
from collections.abc import Generator
from models.model import User, Wallet, Base # Import models to register metadata
from repositories.repository import BaseRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# 1. Use an isolated test database (SQLite in-memory or a dedicated test Postgres URL)
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed only for SQLite
)
TestingSessionLocal = sessionmaker(
    bind=test_engine, autoflush=False, autocommit=False
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
  """Creates all database tables once for the entire test session,"""
  # and drops them after all tests complete.
  Base.metadata.create_all(bind=test_engine)
  yield
  Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
  """Provides a transactional database session per test function.

  Rolls back all changes at the end of each test so the database stays pure.
  """
  connection = test_engine.connect()
  transaction = connection.begin()
  session = TestingSessionLocal(bind=connection)

  yield session

  session.close()
  transaction.rollback()
  connection.close()