from typing import List
from typing import Optional
from enum import Enum
from datetime import datetime
from sqlalchemy import SmallInteger, func, CheckConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class StatusType(str, Enum):
    ACTIVE = "ACTIVE"
    REVIEW = "IN REVIEW"
    INACTIVE = "INACTIVE"


class TransactionStatusType(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False
    )


    user_profile: Mapped["UserProfile"] = relationship(back_populates="user",  uselist=False)
    wallet: Mapped[List["Wallet"]] = relationship(back_populates="user")
    transaction: Mapped[List["Transaction"]] = relationship(back_populates="user")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)    
    first_name: Mapped[Optional[str]] = mapped_column(String(255))
    last_name: Mapped[Optional[str]] = mapped_column(String(255))

    user: Mapped["User"] = relationship(back_populates="user_profile")


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    wallet_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[StatusType] = mapped_column(
        SQLEnum(StatusType),
        default=StatusType.ACTIVE,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="wallet")
    wallet_address: Mapped[List["WalletAddress"]] = relationship(back_populates="wallet")


class WalletAddress(Base):
    __tablename__ = "wallet_addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"), nullable=False)
    blockchain: Mapped[str] = mapped_column(String(50), nullable=False)
    public_address: Mapped[str] = mapped_column(String(255), nullable=False)
    derivation_path: Mapped[Optional[str]] = mapped_column(String(255))
 
    wallet: Mapped["Wallet"] = relationship(back_populates="wallet_address")
    transaction: Mapped[List["Transaction"]] = relationship(back_populates="wallet_address")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    sender_wallet: Mapped[int] = mapped_column(ForeignKey("wallet_addresses.id"), nullable=False)
    recipient_wallet: Mapped[str] = mapped_column(String(255), nullable=False)
    transaction_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False
    )
    fee: Mapped[Optional[float]] = mapped_column(nullable=True)
    status: Mapped[TransactionStatusType] = mapped_column(
        SQLEnum(TransactionStatusType),
        default=TransactionStatusType.PENDING,
        nullable=False
    )

    wallet_address: Mapped["WalletAddress"] = relationship(back_populates="transaction")
    user: Mapped["User"] = relationship(back_populates="transaction")


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    exp_month: Mapped[int] = mapped_column(
        SmallInteger, 
        nullable=False
    )
    exp_year: Mapped[int] = mapped_column(
        SmallInteger, 
        nullable=False
    )    
    card_brand: Mapped[str] = mapped_column(String(255), nullable=False)
    last_four: Mapped[str] = mapped_column(String(4), nullable=False)
    encrypted_pan: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint("exp_month BETWEEN 1 AND 12", name="check_valid_exp_month"),
        CheckConstraint("exp_year >= 2026", name="check_valid_exp_year"),
    )