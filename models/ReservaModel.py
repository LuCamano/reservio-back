from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import TIMESTAMP, Enum, Field, SQLModel

from models.types import ReservaStatus


## Modelo de Reserva
class ReservaBase(SQLModel):
    inicio: datetime = Field(nullable=False, sa_type=TIMESTAMP)
    fin: datetime = Field(nullable=False, sa_type=TIMESTAMP)
    cant_horas: int = Field(default=0, nullable=False)
    fecha_creacion: datetime = Field(default=datetime.now(), sa_type=TIMESTAMP)
    costo_pagado: int = Field(default=0)
    costo_total: int = Field(default=0)
    estado: ReservaStatus = Field(default=ReservaStatus.pendiente, sa_type=Enum(ReservaStatus))
    cliente_id: Optional[UUID] = Field(default=None, foreign_key="usuario.id")
    propiedad_id: Optional[UUID] = Field(default=None, foreign_key="propiedad.id")
    