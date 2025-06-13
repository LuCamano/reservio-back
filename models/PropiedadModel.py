from typing import Optional
from uuid import UUID
import uuid
from sqlmodel import TEXT, Field, Relationship, SQLModel
from models.ComunaModel import Comuna


## Modelo de Propiedad
class PropiedadBase(SQLModel):
    nombre: Optional[str] = Field(max_length=200, default=None, nullable=True)
    descripcion: str = Field(nullable=False, sa_type=TEXT)
    direccion: str = Field(max_length=300, nullable=False)
    tipo: str = Field(max_length=50, nullable=False)
    cod_postal: str = Field(max_length=10, nullable=False)
    capacidad: Optional[int] = Field(default=None, nullable=True)
    precio_hora: int = Field(default=0, nullable=False)
    comuna_id: Optional[UUID] = Field(default=None, foreign_key="comuna.id")
    
class Propiedad(PropiedadBase, table=True):
    __tablename__ = "propiedad"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    activo: bool = Field(default=True)
    comuna: Optional[Comuna] = Relationship(back_populates=None)