from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
# Notes-:
# 1) create_engine → Ye SQLAlchemy ka function hai jo database connection create karta hai.
# 2) declarative_base-: Ye base class provide karta hai jisse hum apne ORM models define kar sakte hain.
# 3) sessionmaker-: Ye database sessions create karne ke liye factory function hai.

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")


if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False,autoflush=False, bind=engine)
Base =  declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()