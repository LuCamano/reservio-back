from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import TIMESTAMP, Field, SQLModel



## Modelo de boleta
class BoletaBase(SQLModel):
    emision: datetime = Field(default_factory=datetime.now, sa_type=TIMESTAMP)
    total: int = Field(default=0, nullable=False)
    reserva_id: Optional[UUID] = Field(default=None, foreign_key="reserva.id")
    