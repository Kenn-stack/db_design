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

session = SessionLocal()
fake = Faker()


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = session
        sqlalchemy_session_persistence = "flush"


class UserFactory(BaseFactory):
    class Meta:
        model = User

    email = factory.LazyAttribute(
            lambda o: f"{fake.first_name().lower()}.{fake.last_name().lower()}@example.com"
    )    
    password = factory.LazyAttribute(
            lambda o: generate_password_hash(fake.password())
    )


class UserProfileFactory(BaseFactory):

    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)

    first_name = factory.LazyAttribute(
        lambda o: o.user.email.split("@")[0].split(".")[0].capitalize()
    )
    last_name = factory.LazyAttribute(
        lambda o: o.user.email.split("@")[0].split(".")[1].capitalize()
    )


class WalletFactory(BaseFactory):
    class Meta:
        model = Wallet

    user = factory.SubFactory(UserFactory)
    wallet_name = factory.LazyAttribute(
      lambda o: (
          f"{o.user.email.split('.')[0].capitalize()}'s"
          f" {random.choice(['Main Vault', 'Trading Wallet', 'Savings', 'DeFi Stash'])}"
      )
    )
    status = factory.Iterator([StatusType.ACTIVE, StatusType.REVIEW, StatusType.INACTIVE])


class WalletAddressFactory(BaseFactory):
    class Meta:
        model = WalletAddress

    public_address = factory.Faker("uuid4")
    blockchain = factory.Iterator(["Ethereum", "Bitcoin", "Binance Smart Chain", "Solana", "Polygon"])
    derivation_path = factory.LazyAttribute(
        lambda o: f"m/44'/{fake.random_int(min=0, max=100)}'/0'/0/{fake.random_int(min=0, max=100)}"
    )


class TransactionFactory(BaseFactory):
    class Meta:
        model = Transaction


    recipient_wallet = factory.Faker("uuid4")
    transaction_hash = factory.LazyAttribute(lambda o: f"0x{fake.sha256()}")    
    amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    status = factory.Iterator([TransactionStatusType.PENDING, TransactionStatusType.CONFIRMED, TransactionStatusType.FAILED])
    fee = factory.LazyAttribute(
      lambda o: (o.amount * Decimal("0.10")).quantize(Decimal("0.01"))
    )
    timestamp = factory.Sequence(generate_steady_timestamp)

    



