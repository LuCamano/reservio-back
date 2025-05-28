from datetime import datetime
from typing import Optional
from uuid import UUID
import uuid

from sqlmodel import TIMESTAMP, Enum, Field, SQLModel

from models.types import ReservaStatus


## Modelo de Reserva
class ReservaBase(SQLModel):
    inicio: datetime = Field(nullable=False, sa_type=TIMESTAMP)
    fin: datetime = Field(nullable=False, sa_type=TIMESTAMP)
    cant_horas: int = Field(default=0, nullable=False)
    estado: ReservaStatus = Field(default="pendiente", sa_type=Enum(ReservaStatus))
    cliente_id: Optional[UUID] = Field(default=None, foreign_key="usuario.id")
    propiedad_id: Optional[UUID] = Field(default=None, foreign_key="propiedad.id")
    
class Reserva(ReservaBase, table=True):
    __tablename__ = "reserva"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    fecha_creacion: datetime = Field(default=datetime.now(), sa_type=TIMESTAMP)
    