from typing import Any, TypeVar

from database import SessionLocal
from models.model import Base, Transaction, TransactionStatusType, User, Wallet, WalletAddress
from loggings.logging import logger
from typing import Any, Generic, Sequence, TypeVar
from loggings.logging import logger
from models.model import Base
from sqlalchemy import select
from sqlalchemy.orm import Session

# Binds the generic variable strictly to your Declarative Base models
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic base repository providing full CRUD operations for any SQLAlchemy model."""

    def __init__(self, model_cls: type[ModelType], session: Session):
        self.model_cls = model_cls
        self.session = session
        self.model_name = model_cls.__name__


    def create(self, instance: ModelType) -> ModelType:
        """Persists a new model record."""
        try:
            logger.info(f"Creating {self.model_name}: {instance}")
            self.session.add(instance)
            self.session.commit()
            self.session.refresh(instance)
            logger.info(f"Successfully created {self.model_name} (ID: {instance.id})")
            return instance
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating {self.model_name}: {e}", exc_info=True)
            raise e


    def get_by_id(self, record_id: int) -> ModelType | None:
        """Retrieves a single record by its primary key ID."""
        try:
            logger.info(f"Retrieving {self.model_name} by ID: {record_id}")
            record = self.session.get(self.model_cls, record_id)
            if record:
                logger.info(f"Found {self.model_name}: {record}")
            else:
                logger.warning(
                    f"{self.model_name} with ID {record_id} does not exist."
                )
            return record
        except Exception as e:
            logger.error(
                f"Error fetching {self.model_name} with ID {record_id}: {e}",
                exc_info=True,
            )
            raise e


    def get_all(self, limit: int = 100, offset: int = 0) -> Sequence[ModelType]:
        """Retrieves all records with pagination."""
        try:
            stmt = select(self.model_cls).offset(offset).limit(limit)
            return self.session.scalars(stmt).all()
        except Exception as e:
            logger.error(f"Error fetching {self.model_name} records: {e}")
            raise e


    def update(self, record_id: int, **kwargs: Any) -> ModelType | None:
        """Dynamically updates attributes of an existing record."""
        try:
            record = self.get_by_id(record_id)
            if not record:
                return None

            valid_columns = set(self.model_cls.__table__.columns.keys())
            for field, value in kwargs.items():
                if field in valid_columns and value is not None:
                    setattr(record, field, value)

            self.session.commit()
            self.session.refresh(record)
            logger.info(f"Updated {self.model_name} with ID {record_id}")
            return record
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating {self.model_name} ID {record_id}: {e}")
            raise e


    def delete(self, record_id: int) -> bool:
        """Deletes a record by ID."""
        try:
            record = self.get_by_id(record_id)
            if not record:
                return False

            self.session.delete(record)
            self.session.commit()
            logger.info(f"Deleted {self.model_name} with ID {record_id}")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting {self.model_name} ID {record_id}: {e}")
            raise e



class UserRepository(BaseRepository[User]):
    """Repository for managing User records in the database."""

    def __init__(self, session: Session):
        super().__init__(model_cls=User, session=session)



class WalletRepository(BaseRepository[Wallet]):
    """Repository for managing Wallet records in the database."""

    def __init__(self, session: Session):
        super().__init__(model_cls=Wallet, session=session)

                    
class WalletAddressRepository(BaseRepository[WalletAddress]):
    """Repository for managing WalletAddress records in the database."""

    def __init__(self, session: Session):
        super().__init__(model_cls=WalletAddress, session=session)


class TransactionRepository(BaseRepository[Transaction]):
    """Repository for managing Transaction records in the database."""
    
    def __init__(self, session: Session):
        super().__init__(model_cls=Transaction, session=session)


    def transfer(self, amount, sender_id, recipient_id):
        """Handles the transfer of funds between two wallets."""
        try:
            from_wallet = self.session.get(Wallet, sender_id)
            to_wallet = self.session.get(Wallet, recipient_id)
            if not from_wallet or not to_wallet:
                raise ValueError("One or both wallets do not exist.")

            if from_wallet.balance < amount:
                raise ValueError("Insufficient funds in the source wallet.")

            # Deduct from source wallet
            from_wallet.balance -= amount
            # Add to destination wallet
            to_wallet.balance += amount

            # Create a transaction record
            transaction = Transaction(
                amount=amount,
                from_wallet_id=from_wallet.id,
                to_wallet_id=to_wallet.id,
                status=TransactionStatusType.COMPLETED
            )
            self.session.add(transaction)
            self.session.commit()
            logger.info(f"Transferred {amount} from Wallet {from_wallet.id} to Wallet {to_wallet.id}")
            return transaction
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error during transfer: {e}", exc_info=True)
            raise e