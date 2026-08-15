from database import SessionLocal
from repositories.repository import UserRepository

session = SessionLocal()

# Get a user by ID
user_repo = UserRepository(session)
user = user_repo.get_by_id(1)
print(user)