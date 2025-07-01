from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import TIMESTAMP, Enum, Field, SQLModel, TEXT

from models.types import ComisionStatus


## Modelo de Comisión
class ComisionBase(SQLModel):
    monto: int = Field(nullable=False)  # Monto de la comisión en centavos
    porcentaje: float = Field(default=5.0, nullable=False)  # Porcentaje de comisión (5%)
    estado: ComisionStatus = Field(default=ComisionStatus.pendiente, sa_type=Enum(ComisionStatus))
    fecha_creacion: datetime = Field(default_factory=datetime.now, sa_type=TIMESTAMP)
    fecha_procesamiento: Optional[datetime] = Field(default=None, sa_type=TIMESTAMP)
    descripcion: Optional[str] = Field(default=None, sa_type=TEXT)
    pago_id: UUID = Field(foreign_key="pago.id", nullable=False)
    propietario_id: UUID = Field(foreign_key="usuario.id", nullable=False)  # ID del propietario que debe recibir el pago
