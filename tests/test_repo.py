from models.model import StatusType, User, Wallet, WalletAddress
import pytest
from repositories.repository import TransactionRepository, UserRepository, WalletAddressRepository, WalletRepository
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




def test_transfer(db_session: Session):


  # Arrange
  user_repo = UserRepository(session=db_session)

  wallet_repo = WalletRepository(session=db_session)
  wallet_address_repo = WalletAddressRepository(session=db_session)
  transaction_repo = TransactionRepository(session=db_session)

  #create a user
  new_user = user_repo.create(User(password="Ekene", email="ekene@example.com"))

  # Create two wallets and their addresses
  wallet1 = wallet_repo.create(Wallet(user=new_user, balance=1000, wallet_name="Sender Wallet", status=StatusType.ACTIVE))
  wallet2 = wallet_repo.create(Wallet(user=new_user, balance=500, wallet_name="Recipient Wallet", status=StatusType.ACTIVE))

  address1 = wallet_address_repo.create(WalletAddress(wallet=wallet1, public_address="address1", blockchain="Ethereum", derivation_path="m/44'/60'/0'/0/0"))
  address2 = wallet_address_repo.create(WalletAddress(wallet=wallet2, public_address="address2", blockchain="Ethereum", derivation_path="m/44'/60'/0'/0/1"))

  # Act
  amount_to_transfer = 200
  transaction = transaction_repo.transfer(user_id=new_user.id, amount=amount_to_transfer, sender_wallet_address="address1", recipient_wallet_address="address2")

  # Assert
  updated_wallet1 = wallet_repo.get_by_id(wallet1.id)
  updated_wallet2 = wallet_repo.get_by_id(wallet2.id)

  assert updated_wallet1.balance == 1000 - amount_to_transfer - (amount_to_transfer * 0.02)  # Deducted amount + fee
  assert updated_wallet2.balance == 500 + amount_to_transfer  # Added amount
  assert transaction.amount == amount_to_transfer