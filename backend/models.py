# backend/models.py
from datetime import datetime

from backend.database import Base
from sqlalchemy import Column, DateTime, Integer, LargeBinary, String


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    secret = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<User {self.email}>"
