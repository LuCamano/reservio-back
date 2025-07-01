from typing import Optional
from uuid import UUID
from sqlmodel import TEXT, Field, SQLModel
from datetime import time

## Modelo de Propiedad
class PropiedadBase(SQLModel):
    nombre: Optional[str] = Field(max_length=200, default=None, nullable=True)
    descripcion: str = Field(nullable=False, sa_type=TEXT)
    direccion: str = Field(max_length=300, nullable=False)
    tipo: str = Field(max_length=50, nullable=False)
    cod_postal: str = Field(max_length=10, nullable=False)
    capacidad: Optional[int] = Field(default=None, nullable=True)
    precio_hora: int = Field(default=0, nullable=False)
    hora_apertura: Optional[time] = Field(default=None, nullable=True)
    hora_cierre: Optional[time] = Field(default=None, nullable=True)
    comuna_id: Optional[UUID] = Field(default=None, foreign_key="comuna.id")
