from datetime import datetime
from typing import Optional
from uuid import UUID
import uuid
from sqlmodel import SQLModel, Field, TIMESTAMP


class TokenBlacklist(SQLModel, table=True):
    __tablename__ = "token_blacklist"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    token_jti: str = Field(max_length=255, nullable=False, unique=True, index=True)  # JWT ID
    token_type: str = Field(max_length=20, nullable=False)  # 'access' or 'refresh'
    user_email: str = Field(max_length=150, nullable=False)
    blacklisted_at: datetime = Field(default_factory=datetime.now, sa_type=TIMESTAMP)
    expires_at: datetime = Field(nullable=False, sa_type=TIMESTAMP)
