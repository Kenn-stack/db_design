from .connect import SessionLocal
from .model import User

with SessionLocal() as session:
    new_user = User(email="fake@email.com", password="password")
    session.add(new_user)
    session.commit()
