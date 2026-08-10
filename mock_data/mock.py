from decimal import Decimal

import factory
import random
from datetime import datetime
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from werkzeug.security import generate_password_hash

from models.model import StatusType, Transaction, TransactionStatusType, User, UserProfile, Wallet, WalletAddress
from mock_data.utils import generate_steady_timestamp
from database import SessionLocal

# Global SQLAlchemy database session instance for factoryboy model persistence
session = SessionLocal()
fake = Faker()


class BaseFactory(SQLAlchemyModelFactory):
    """Abstract base factory configuring shared SQLAlchemy session persistence for all model factories."""

    class Meta:
        abstract = True
        sqlalchemy_session = session
        sqlalchemy_session_persistence = "flush"


class UserFactory(BaseFactory):
    """Factory for generating mock User records with hashed passwords and matching email addresses."""

    class Meta:
        model = User

    # Generates email address matching fake user names to keep user profile data consistent
    email = factory.LazyAttribute(
            lambda o: f"{fake.first_name().lower()}.{fake.last_name().lower()}@example.com"
    )    
    # Hashes generated password string using standard Werkzeug security utilities
    password = factory.LazyAttribute(
            lambda o: generate_password_hash(fake.password())
    )


class UserProfileFactory(BaseFactory):
    """Factory for generating UserProfile records synchronized with an associated User's email."""

    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)

    # Derives first name directly from the generated user email local-part
    first_name = factory.LazyAttribute(
        lambda o: o.user.email.split("@")[0].split(".")[0].capitalize()
    )
    # Derives last name directly from the generated user email local-part
    last_name = factory.LazyAttribute(
        lambda o: o.user.email.split("@")[0].split(".")[1].capitalize()
    )


class WalletFactory(BaseFactory):
    """Factory for generating user Wallet containers with realistic names and rotating statuses."""

    class Meta:
        model = Wallet

    user = factory.SubFactory(UserFactory)
    # Generates realistic wallet names dynamically bound to the user's first name
    wallet_name = factory.LazyAttribute(
      lambda o: (
          f"{o.user.email.split('.')[0].capitalize()}'s"
          f" {random.choice(['Main Vault', 'Trading Wallet', 'Savings', 'DeFi Stash'])}"
      )
    )
    # Rotates wallet status across defined enum states sequentially
    status = factory.Iterator([StatusType.ACTIVE, StatusType.REVIEW, StatusType.INACTIVE])


class WalletAddressFactory(BaseFactory):
    """Factory for generating multi-chain public blockchain addresses and derivation paths."""

    class Meta:
        model = WalletAddress

    public_address = factory.Faker("uuid4")
    # Cycles through supported blockchain networks
    blockchain = factory.Iterator(["Ethereum", "Bitcoin", "Binance Smart Chain", "Solana", "Polygon"])
    # Generates HD wallet derivation path format (BIP-44 standard)
    derivation_path = factory.LazyAttribute(
        lambda o: f"m/44'/{fake.random_int(min=0, max=100)}'/0'/0/{fake.random_int(min=0, max=100)}"
    )


class TransactionFactory(BaseFactory):
    """Factory for generating ledger transactions with calculated fees and sequential timestamps."""

    class Meta:
        model = Transaction

    recipient_wallet = factory.Faker("uuid4")
    # Simulates a 256-bit hexadecimal blockchain transaction hash
    transaction_hash = factory.LazyAttribute(lambda o: f"0x{fake.sha256()}")    
    amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    # Cycles through transaction lifecycle statuses
    status = factory.Iterator([TransactionStatusType.PENDING, TransactionStatusType.CONFIRMED, TransactionStatusType.FAILED])
    # Calculates a fixed 10% fee rounded to two decimal places relative to transfer amount
    fee = factory.LazyAttribute(
      lambda o: (o.amount * Decimal("0.10")).quantize(Decimal("0.01"))
    )
    # Generates steadily advancing chronological timestamps across records
    timestamp = factory.Sequence(generate_steady_timestamp)