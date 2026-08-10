import random

from sqlalchemy import text

from .mock import TransactionFactory, UserFactory, UserProfileFactory, WalletAddressFactory, WalletFactory, session
from models.model import Transaction, User, UserProfile, Wallet, WalletAddress
from loggings.logging import logger


def reset_db():
    """Truncates all target tables and resets primary key auto-increment sequences before ingestion."""
    logger.info("Truncating existing tables...")
    # TRUNCATE ... CASCADE clears table contents and resets ID auto-increment counters
    session.execute(
        text(
            "TRUNCATE TABLE transactions, wallet_addresses, wallets,"
            " user_profiles, users RESTART IDENTITY CASCADE;"
        )
    )
    session.commit()


def insert_user() -> list[User]:
    """Generates and flushes a batch of 50 mock User instances."""
    users = UserFactory.create_batch(50)
    return users

def insert_user_profile(users) -> list[UserProfile]:
    """Creates a 1:1 corresponding UserProfile record for each User in the provided list."""
    profiles = []

    for user in users:
        profile = UserProfileFactory(user=user)
        profiles.append(profile)

    return profiles


def insert_wallets(users) -> list[Wallet]:
    """Generates 100 Wallet instances randomly distributed across the provided users."""
    wallets = []

    for _ in range(100):
        # Randomly assigns each wallet to an existing user
        wallet = WalletFactory(user=random.choice(users))
        wallets.append(wallet)

    return wallets


def insert_wallet_addresses(wallets) -> list[WalletAddress]:
    """Generates 150 blockchain WalletAddress instances randomly assigned to existing wallets."""
    wallet_addresses = []

    for _ in range(150):
        # Randomly assigns each address record to a parent wallet
        wallet_address = WalletAddressFactory(wallet=random.choice(wallets))
        wallet_addresses.append(wallet_address)

    return wallet_addresses


def insert_transactions(users, wallet_addresses) -> list[Transaction]:
    """Generates 200 Transaction records ensuring user ownership matches the sender's wallet address."""
    transactions = []

    for _ in range(200):
        wallet_address = random.choice(wallet_addresses)

        # Binds the transaction user directly to the owner of the selected sender wallet address
        transaction = TransactionFactory(
            user=wallet_address.wallet.user,
            wallet_address=wallet_address
        )
        transactions.append(transaction)

    return transactions


if __name__ == "__main__":
    try:
        # Wipe existing database tables before starting batch ingestion
        reset_db()
        
        logger.info("Starting database mock data ingestion...")

        # Ingestion Pipeline: Insert dependent entities sequentially
        logger.info("Inserting users...")
        users = insert_user()
        logger.info(f"Successfully inserted {len(users)} users.")

        logger.info("Inserting user profiles...")
        profiles = insert_user_profile(users)
        logger.info(f"Successfully inserted {len(profiles)} user profiles.")

        logger.info("Inserting wallets...")
        wallets = insert_wallets(users)
        logger.info(f"Successfully inserted {len(wallets)} wallets.")

        logger.info("Inserting wallet addresses...")
        wallet_addresses = insert_wallet_addresses(wallets)
        logger.info(
            f"Successfully inserted {len(wallet_addresses)} wallet addresses."
        )

        logger.info("Inserting transactions...")
        transactions = insert_transactions(users, wallet_addresses)
        logger.info(f"Successfully inserted {len(transactions)} transactions.")

        # Persist all generated records across all tables in a single transaction block
        logger.info("Committing transaction to database...")
        session.commit()
        logger.info("Database commit successful. All mock data inserted!")

    except Exception as e:
        # Safely rollback active transaction on failure to maintain database consistency
        logger.error(
            f"An error occurred during database insert. Rolling back... Details: {e}",
            exc_info=True,
        )
        session.rollback()


# Legacy execution block kept for reference:
# if __name__ == "__main__":
#     users = insert_user()
#     profiles = insert_user_profile(users)
#     wallets = insert_wallets(users)
#     wallet_addresses = insert_wallet_addresses(wallets)
#     transactions = insert_transactions(users, wallet_addresses)

#     session.commit()