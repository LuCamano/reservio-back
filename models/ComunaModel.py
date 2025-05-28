from typing import Optional
from uuid import UUID
import uuid
from sqlmodel import SQLModel, Field


## Modelo de Comuna
class ComunaBase(SQLModel):
    nombre: str = Field(max_length=100, nullable=False, unique=True)
    region_id: Optional[UUID] = Field(default=None, foreign_key="region.id")
    
class Comuna(ComunaBase, table=True):
    __tablename__ = "comuna"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)