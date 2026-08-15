from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env if present


db_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://root:root@localhost:5432/db_design")

engine = create_engine(db_url, echo=True)
    
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# Create tables in PostgreSQL
# Base.metadata.create_all(engine)