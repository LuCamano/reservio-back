from datetime import datetime, date
from typing import List, Optional
from uuid import UUID
import uuid
from sqlmodel import JSON, Column, Field, Relationship, TIMESTAMP, SQLModel

from models.types import UserType
from .UsuarioModel import UsuarioBase
from .ComunaModel import ComunaBase
from .RegionModel import RegionBase
from .PropiedadModel import PropiedadBase
from .ReservaModel import ReservaBase
from .BoletaModel import BoletaBase
from .ValoracionModel import ValoracionBase
from .manyToMany import UsuarioPropiedad

# Clases tabla (heredan de su base)
class Usuario(UsuarioBase, table=True):
    __tablename__ = "usuario"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    fecha_creacion: date = Field(default=date.today())
    activo: bool = Field(default=True)
    propiedades: list["Propiedad"] = Relationship(link_model=UsuarioPropiedad, back_populates="propietarios")

class Region(RegionBase, table=True):
    __tablename__ = "region"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    comunas: list["Comuna"] = Relationship(back_populates="region")

class Comuna(ComunaBase, table=True):
    __tablename__ = "comuna"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    region: Region = Relationship(back_populates="comunas")
    propiedades: list["Propiedad"] = Relationship(back_populates="comuna")

class Propiedad(PropiedadBase, table=True):
    __tablename__ = "propiedad"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    activo: bool = Field(default=True)
    imagenes: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))
    comuna: Optional[Comuna] = Relationship(back_populates="propiedades")
    propietarios: list["Usuario"] = Relationship(link_model=UsuarioPropiedad, back_populates="propiedades")
    valoraciones: list["Valoracion"] = Relationship(back_populates="propiedad")

class Reserva(ReservaBase, table=True):
    __tablename__ = "reserva"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    fecha_creacion: datetime = Field(default=datetime.now(), sa_type=TIMESTAMP)
    boleta: Optional["Boleta"] = Relationship(back_populates="reserva")

class Boleta(BoletaBase, table=True):
    __tablename__ = "boleta"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    reserva: Optional[Reserva] = Relationship(back_populates="boleta")

class Valoracion(ValoracionBase, table=True):
    __tablename__ = "valoracion"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    propiedad: Optional[Propiedad] = Relationship(back_populates="valoraciones")
    cliente: Optional[Usuario] = Relationship()
    
## Clases de lectura (heredan de su base)
class UsuarioRead(SQLModel):
    id: UUID
    email: str
    rut: str
    nombres: str
    appaterno: str
    apmaterno: str
    fecha_nacimiento: date
    tipo: UserType
    fecha_creacion: date
    activo: bool
    propiedades: list["Propiedad"] = []
    