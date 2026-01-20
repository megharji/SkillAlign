from sqlalchemy import Column, Integer, String, DateTime
from app.common.config import Base
from datetime import datetime
from sqlalchemy.orm import relationship

# Notes-: 

# 1) primary_key = True -: 
#    a) Ensures each row is uniquely identifiable.
#    b) Automatically creates an index for faster lookups.
# 2) index = True -:
#    a) Creates an index on the column to speed up query performance.
# 3) unique = True -:
#    a) Ensures all values in the column are distinct.
#    b) Prevents duplicate entries in the column.
# 4) nullable = False -:
#    a) Ensures the column cannot have NULL values.
#  5) default=datetime.utcnow -:
#    a) Sets the default value of the column to the current UTC date and time when a new record is created.

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

