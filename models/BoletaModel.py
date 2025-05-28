from datetime import datetime
from typing import Optional
from uuid import UUID
import uuid
from sqlmodel import TIMESTAMP, Field, Relationship, SQLModel

from models.ReservaModel import Reserva


## Modelo de boleta
class BoletaBase(SQLModel):
    emision: datetime = Field(default=datetime.now(), sa_type=TIMESTAMP)
    total: int = Field(default=0, nullable=False)
    reserva_id: Optional[UUID] = Field(default=None, foreign_key="reserva.id")
    
class Boleta(BoletaBase, table=True):
    __tablename__ = "boleta"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    reserva: Optional[Reserva] = Relationship(back_populates="boleta")
    