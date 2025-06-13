from sqlmodel import SQLModel, Field, TIMESTAMP
from datetime import datetime
from uuid import UUID
from typing import Optional

## Intersection table for many-to-many relationship between Usuario and Propiedad
class UsuarioPropiedad(SQLModel, table=True):
    __tablename__ = "usuario_propiedad"
    usuario_id: UUID = Field(foreign_key="usuario.id", primary_key=True)
    propiedad_id: UUID = Field(foreign_key="propiedad.id", primary_key=True)
    fecha_inicio: datetime = Field(default=datetime.now(), sa_type=TIMESTAMP)
    fecha_termino: Optional[datetime] = Field(default=None, nullable=True, sa_type=TIMESTAMP)