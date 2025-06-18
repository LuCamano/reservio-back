from typing import Optional
from uuid import UUID
from sqlmodel import SQLModel, Field


## Modelo de Comuna
class ComunaBase(SQLModel):
    nombre: str = Field(max_length=100, nullable=False, unique=True)
    region_id: Optional[UUID] = Field(default=None, foreign_key="region.id")