from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

from models.types import PagoStatus, ComisionStatus


# Schemas para respuestas de la API de pagos

class PagoResponse(BaseModel):
    id: UUID
    monto_total: int
    monto_propietario: int
    monto_comision: int
    estado: PagoStatus
    fecha_creacion: datetime
    fecha_procesamiento: Optional[datetime] = None
    mp_payment_id: Optional[str] = None
    mp_preference_id: Optional[str] = None
    mp_status: Optional[str] = None

class PreferenciaPagoResponse(BaseModel):
    pago_id: str
    preference_id: str
    init_point: str
    sandbox_init_point: str

class ComisionResponse(BaseModel):
    id: UUID
    monto: int
    porcentaje: float
    estado: ComisionStatus
    fecha_creacion: datetime
    fecha_procesamiento: Optional[datetime] = None
    descripcion: Optional[str] = None
    pago_id: UUID
    propietario_id: UUID

class PropietarioComisionResponse(BaseModel):
    propietario: dict
    comisiones: List[dict]
    monto_total: int

class ResumenComisionesResponse(BaseModel):
    periodo: dict
    total_comisiones: int
    cantidad_total: int
    por_estado: dict

class ApiResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None
