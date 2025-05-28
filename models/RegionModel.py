from typing import Optional
from uuid import UUID
import uuid
from sqlmodel import SQLModel, Field


## Modelo de Region
class RegionBase(SQLModel):
    nombre: str = Field(max_length=100, nullable=False, unique=True)

class Region(RegionBase, table=True):
    __tablename__ = "region"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)