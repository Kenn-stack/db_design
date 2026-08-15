from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import CheckConstraint, ForeignKey, Index, SmallInteger, String, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class StatusType(str, Enum):
  ACTIVE = "ACTIVE"
  REVIEW = "IN REVIEW"
  INACTIVE = "INACTIVE"


class TransactionStatusType(str, Enum):
  PENDING = "PENDING"
  CONFIRMED = "CONFIRMED"
  FAILED = "FAILED"


class KYCStatusType(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class Base(DeclarativeBase):
  pass


class User(Base):
  """Represents a registered platform user account."""

  __tablename__ = "users"

  id: Mapped[int] = mapped_column(
      primary_key=True,
      comment="Unique primary key identifier for the user",
  )
  email: Mapped[str] = mapped_column(
      String(255),
      unique=True,
      nullable=False,
      comment="Unique email address used for account identification and login",
  )
  password: Mapped[str] = mapped_column(
      String(255),
      nullable=False,
      comment="Hashed security credentials for account authentication",
  )
  created_at: Mapped[datetime] = mapped_column(
      server_default=func.now(),
      nullable=False,
      comment="UTC timestamp when the user account was created",
  )

  user_profile: Mapped["UserProfile"] = relationship(
      back_populates="user", uselist=False
  )
  wallet: Mapped[List["Wallet"]] = relationship(back_populates="user")
  transaction: Mapped[List["Transaction"]] = relationship(back_populates="user")

  def __repr__(self) -> str:
    return f"<User id={self.id}, email={self.email!r}>"


class UserProfile(Base):
  """Stores personal identity, KYC compliance, address, and localization preferences for a user."""

  __tablename__ = "user_profiles"

  id: Mapped[int] = mapped_column(
      primary_key=True,
      comment="Unique primary key identifier for the user profile",
  )
  user_id: Mapped[int] = mapped_column(
      ForeignKey("users.id"),
      unique=True,
      nullable=False,
      comment="Foreign key linking the profile to its owning user",
  )

  # Basic Identity
  first_name: Mapped[Optional[str]] = mapped_column(
      String(255), comment="Legal or given first name"
  )
  last_name: Mapped[Optional[str]] = mapped_column(
      String(255), comment="Legal or family last name"
  )
  phone_number: Mapped[Optional[str]] = mapped_column(
      String(30), unique=True, comment="E.164 formatted phone number for MFA"
  )
  date_of_birth: Mapped[Optional[date]] = mapped_column(
      comment="Legal date of birth for age verification"
  )

  # KYC & Compliance
  country_code: Mapped[Optional[str]] = mapped_column(
      String(3), comment="ISO 3166-1 alpha-3 country code (e.g. NGA, USA)"
  )
  kyc_status: Mapped[KYCStatusType] = mapped_column(
      SQLEnum(KYCStatusType, native_enum=False),
      default=KYCStatusType.NOT_STARTED,
      nullable=False,
      comment="Identity verification status",
  )
  kyc_level: Mapped[int] = mapped_column(
      SmallInteger, default=0, nullable=False, comment="Verification tier level"
  )

  # Address Details
  address_line1: Mapped[Optional[str]] = mapped_column(String(255))
  city: Mapped[Optional[str]] = mapped_column(String(100))
  postal_code: Mapped[Optional[str]] = mapped_column(String(20))

  # Preferences & Localization
  preferred_fiat_currency: Mapped[str] = mapped_column(
      String(3), default="USD", nullable=False, comment="Display fiat currency"
  )
  timezone: Mapped[str] = mapped_column(
      String(50), default="UTC", nullable=False, comment="User preferred timezone"
  )

  # Timestamps
  updated_at: Mapped[datetime] = mapped_column(
      server_default=func.now(),
      onupdate=func.now(),
      nullable=False,
      comment="UTC timestamp when profile was last updated",
  )

  user: Mapped["User"] = relationship(back_populates="user_profile")


class Wallet(Base):
  """Represents a user's wallet container for holding multi-chain asset addresses."""

  __tablename__ = "wallets"

  id: Mapped[int] = mapped_column(
      primary_key=True,
      comment="Unique primary key identifier for the wallet",
  )
  user_id: Mapped[int] = mapped_column(
      ForeignKey("users.id"),
      nullable=False,
      comment="Foreign key linking the wallet to its owning user",
  )
  wallet_name: Mapped[str] = mapped_column(
      String(255),
      nullable=False,
      comment="User-defined label or display name for the wallet",
  )
  status: Mapped[StatusType] = mapped_column(
      SQLEnum(StatusType),
      default=StatusType.ACTIVE,
      nullable=False,
      comment="Operational status of the wallet: ACTIVE, IN REVIEW, or INACTIVE",
  )
  created_at: Mapped[datetime] = mapped_column(
      server_default=func.now(),
      nullable=False,
      comment="UTC timestamp when the wallet was created",
  )

  user: Mapped["User"] = relationship(back_populates="wallet")
  wallet_address: Mapped[List["WalletAddress"]] = relationship(
      back_populates="wallet"
  )


class WalletAddress(Base):
  """Stores public blockchain addresses associated with a specific wallet."""

  __tablename__ = "wallet_addresses"

  id: Mapped[int] = mapped_column(
      primary_key=True,
      comment="Unique primary key identifier for the wallet address record",
  )
  wallet_id: Mapped[int] = mapped_column(
      ForeignKey("wallets.id"),
      nullable=False,
      comment="Foreign key linking the address to its parent wallet",
  )
  blockchain: Mapped[str] = mapped_column(
      String(50),
      nullable=False,
      comment="Target blockchain network (e.g. Ethereum, Bitcoin, Solana)",
  )
  public_address: Mapped[str] = mapped_column(
      String(255),
      nullable=False,
      comment="On-chain public key or wallet address",
  )
  derivation_path: Mapped[Optional[str]] = mapped_column(
      String(255),
      comment="HD wallet derivation path used to generate the keypair",
  )

  wallet: Mapped["Wallet"] = relationship(back_populates="wallet_address")
  transaction: Mapped[List["Transaction"]] = relationship(
      back_populates="wallet_address"
  )

  __table_args__ = (
      # Standard composite index on (blockchain, id)
      Index("idx_wallet_addresses_blockchain_id", "blockchain", "id"),
  )


class Transaction(Base):
  """Records financial transactions executed across platform wallets."""

  __tablename__ = "transactions"

  id: Mapped[int] = mapped_column(
      primary_key=True,
      comment="Unique primary key identifier for the transaction",
  )
  user_id: Mapped[int] = mapped_column(
      ForeignKey("users.id"),
      nullable=False,
      comment="Foreign key linking the transaction to the initiating user",
  )
  sender_wallet: Mapped[int] = mapped_column(
      ForeignKey("wallet_addresses.id"),
      nullable=False,
      comment="Foreign key pointing to the originating sender's wallet address record",
  )
  recipient_wallet: Mapped[str] = mapped_column(
      String(255),
      nullable=False,
      comment="Public address of the destination recipient",
  )
  transaction_hash: Mapped[str] = mapped_column(
      String(255),
      nullable=False,
      comment="Unique cryptographic transaction hash on the blockchain network",
  )
  amount: Mapped[float] = mapped_column(
      nullable=False,
      comment="Transfer volume in base units",
  )
  timestamp: Mapped[datetime] = mapped_column(
      server_default=func.now(),
      nullable=False,
      comment="UTC timestamp when the transaction occurred",
  )
  fee: Mapped[Optional[float]] = mapped_column(
      nullable=True,
      comment="Network gas or processing fee charged for executing the transaction",
  )
  status: Mapped[TransactionStatusType] = mapped_column(
      SQLEnum(TransactionStatusType),
      default=TransactionStatusType.PENDING,
      nullable=False,
      comment="Current execution state: PENDING, CONFIRMED, or FAILED",
  )

  wallet_address: Mapped["WalletAddress"] = relationship(
      back_populates="transaction"
  )
  user: Mapped["User"] = relationship(back_populates="transaction")

  __table_args__ = (
      # Covering index on sender_wallet that INCLUDES status and fee payload columns
      Index(
          "idx_transactions_sender_status_fee",
          "sender_wallet",
          postgresql_include=["status", "fee"],
      ),
  )


class Card(Base):
  """Stores encrypted payment card credentials for user accounts."""

  __tablename__ = "cards"

  id: Mapped[int] = mapped_column(
      primary_key=True,
      comment="Unique primary key identifier for the payment card record",
  )
  user_id: Mapped[int] = mapped_column(
      ForeignKey("users.id"),
      nullable=False,
      comment="Foreign key linking the payment card to its owning user",
  )
  exp_month: Mapped[int] = mapped_column(
      SmallInteger,
      nullable=False,
      comment="Expiration month represented as an integer (1-12)",
  )
  exp_year: Mapped[int] = mapped_column(
      SmallInteger,
      nullable=False,
      comment="Four-digit expiration year (must be >= 2026)",
  )
  card_brand: Mapped[str] = mapped_column(
      String(255),
      nullable=False,
      comment="Payment network card brand (e.g. Visa, Mastercard)",
  )
  last_four: Mapped[str] = mapped_column(
      String(4),
      nullable=False,
      comment="Last four digits of the primary account number",
  )
  encrypted_pan: Mapped[str] = mapped_column(
      String(255),
      nullable=False,
      comment="Encrypted Primary Account Number payload for secure processing",
  )
  created_at: Mapped[datetime] = mapped_column(
      server_default=func.now(),
      nullable=False,
      comment="UTC timestamp when the payment card was registered",
  )

  __table_args__ = (
      CheckConstraint(
          "exp_month BETWEEN 1 AND 12", name="check_valid_exp_month"
      ),
      CheckConstraint("exp_year >= 2026", name="check_valid_exp_year"),
  )