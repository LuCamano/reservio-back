from typing import Optional
from datetime import date
import uuid
from uuid import UUID
from sqlmodel import SQLModel, Field, Enum, Relationship
from models.PropiedadModel import Propiedad
from models.types import UserType
from models.manyToMany import UsuarioPropiedad

## Modelo de Usuario
class UsuarioBase(SQLModel):
    email: str = Field(max_length=150, nullable=False, unique=True, index=True)
    rut: str = Field(max_length=12, nullable=False, unique=True, index=True)
    nombres: str = Field(max_length=150, nullable=False)
    appaterno: str = Field(max_length=100, nullable=False)
    apmaterno: str = Field(max_length=100, nullable=False)
    fecha_nacimiento: date = Field(nullable=False)
    tipo: UserType = Field(default='cliente', sa_type=Enum(UserType))
    password: str = Field(max_length=100, nullable=False)
    
class Usuario(UsuarioBase, table=True):
    __tablename__ = "usuario"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    fecha_creacion: date = Field(default=date.today())
    activo: bool = Field(default=True)
    propiedades: list["Propiedad"] = Relationship(back_populates="propietarios", link_model=UsuarioPropiedad, sa_relationship_kwargs={"lazy": "selectin"})
    