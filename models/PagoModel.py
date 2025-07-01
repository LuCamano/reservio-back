from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import TIMESTAMP, Enum, Field, SQLModel, TEXT

from models.types import PagoStatus


## Modelo de Pago
class PagoBase(SQLModel):
    monto_total: int = Field(nullable=False)  # Monto total en centavos
    monto_propietario: int = Field(nullable=False)  # 95% del monto
    monto_comision: int = Field(nullable=False)  # 5% del monto
    moneda: str = Field(default="CLP", max_length=3)
    metodo_pago: str = Field(default="mercadopago", max_length=50)
    mp_payment_id: Optional[str] = Field(default=None, max_length=100)  # ID del pago en MercadoPago
    mp_preference_id: Optional[str] = Field(default=None, max_length=100)  # ID de la preferencia
    mp_external_reference: Optional[str] = Field(default=None, max_length=100)  # Referencia externa
    mp_status: Optional[str] = Field(default=None, max_length=50)  # Estado en MercadoPago
    estado: PagoStatus = Field(default=PagoStatus.pendiente, sa_type=Enum(PagoStatus))
    fecha_creacion: datetime = Field(default_factory=datetime.now, sa_type=TIMESTAMP)
    fecha_procesamiento: Optional[datetime] = Field(default=None, sa_type=TIMESTAMP)
    descripcion: Optional[str] = Field(default=None, sa_type=TEXT)
    reserva_id: UUID = Field(foreign_key="reserva.id", nullable=False)
