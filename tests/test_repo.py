from models.model import User
import pytest
from repositories.repository import UserRepository
from sqlalchemy.orm import Session


class TestUserRepository:

  def test_create_user_success(self, db_session: Session):
    # Arrange
    user_repo = UserRepository(session=db_session)
    new_user = User(password="Ekene", email="ekene@example.com")

    # Act
    created = user_repo.create(new_user)

    # Assert
    assert created.id is not None
    assert created.email == "ekene@example.com"
   

  def test_get_by_id_found(self, db_session: Session):
    # Arrange
    user_repo = UserRepository(session=db_session)
    user = user_repo.create(User(password="Alice", email="alice@example.com"))

    # Act
    fetched = user_repo.get_by_id(user.id)

    # Assert
    assert fetched is not None
    assert fetched.id == user.id
    assert fetched.email == "alice@example.com"

  def test_get_by_id_not_found(self, db_session: Session):
    # Arrange
    user_repo = UserRepository(session=db_session)

    # Act
    fetched = user_repo.get_by_id(2000000000)  # Assuming this ID does not exist

    # Assert
    assert fetched is None
    

  def test_update_user_fields(self, db_session: Session):
    # Arrange
    user_repo = UserRepository(session=db_session)
    user = user_repo.create(User(password="Bob", email="bob@example.com"))

    # Act
    updated = user_repo.update(user.id, email="bobbuilder@example.com")

    # Assert
    assert updated is not None
    assert updated.email == "bobbuilder@example.com"

  def test_delete_user(self, db_session: Session):
    # Arrange
    user_repo = UserRepository(session=db_session)
    user = user_repo.create(User(password="Charlie", email="charlie@example.com"))

    # Act
    success = user_repo.delete(user.id)
    fetched_after_delete = user_repo.get_by_id(user.id)

    # Assert
    assert success is True
    assert fetched_after_delete is None

