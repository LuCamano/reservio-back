from sqlmodel import SQLModel, Field, Relationship, TEXT, TIMESTAMP
import enum
from sqlalchemy.types import Enum
import uuid
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from models.manyToMany import UsuarioPropiedad

class UserType(enum.Enum):
    """ Enumerador para el tipo de usuario """
    admin = "admin"
    cliente = "cliente"
    propietario = "propietario"

class ReservaStatus(enum.Enum):
    """ Enumerador para el estado de la reserva """
    pendiente = "pendiente"
    completada = "completada"
    cancelada = "cancelada"

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
    reservas: list["Reserva"] = Relationship(back_populates="cliente", sa_relationship_kwargs={"lazy": "selectin"})
    valoraciones: list["Valoracion"] = Relationship(back_populates="cliente", sa_relationship_kwargs={"lazy": "selectin"})
    propiedades: list["Propiedad"] = Relationship(back_populates="propietarios", link_model=UsuarioPropiedad, sa_relationship_kwargs={"lazy": "selectin"})
    
## Modelo de Region
class RegionBase(SQLModel):
    nombre: str = Field(max_length=100, nullable=False, unique=True)

class Region(RegionBase, table=True):
    __tablename__ = "region"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    comunas: list["Comuna"] = Relationship(back_populates="region", sa_relationship_kwargs={"lazy": "selectin"})
    
## Modelo de Comuna
class ComunaBase(SQLModel):
    nombre: str = Field(max_length=100, nullable=False, unique=True)
    region_id: Optional[UUID] = Field(default=None, foreign_key="region.id")
    
class Comuna(ComunaBase, table=True):
    __tablename__ = "comuna"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    region: Optional[Region] = Relationship(back_populates="comunas")
    propiedades: list["Propiedad"] = Relationship(back_populates="comuna", sa_relationship_kwargs={"lazy": "selectin"})

## Modelo de Propiedad
class PropiedadBase(SQLModel):
    nombre: Optional[str] = Field(max_length=200, default=None, nullable=True)
    descripcion: str = Field(nullable=False, sa_type=TEXT)
    direccion: str = Field(max_length=300, nullable=False)
    cod_postal: str = Field(max_length=10, nullable=False)
    capacidad: Optional[int] = Field(default=None, nullable=True)
    precio_hora: int = Field(default=0, nullable=False)
    comuna_id: Optional[UUID] = Field(default=None, foreign_key="comuna.id")
    
class Propiedad(PropiedadBase, table=True):
    __tablename__ = "propiedad"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    activo: bool = Field(default=True)
    comuna: Optional[Comuna] = Relationship(back_populates="propiedades")
    reservas: list["Reserva"] = Relationship(back_populates="propiedad", sa_relationship_kwargs={"lazy": "selectin"})
    valoraciones: list["Valoracion"] = Relationship(back_populates="propiedad", sa_relationship_kwargs={"lazy": "selectin"})
    propietarios: list["Usuario"] = Relationship(back_populates="propiedades", link_model=UsuarioPropiedad, sa_relationship_kwargs={"lazy": "selectin"})
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
    cliente: Optional[Usuario] = Relationship(back_populates="reservas")
    propiedad: Optional[Propiedad] = Relationship(back_populates="reservas")
    fecha_creacion: datetime = Field(default=datetime.now(), sa_type=TIMESTAMP)
    boleta: Optional["Boleta"] = Relationship(back_populates="reserva")
    
## Modelo de boleta
class BoletaBase(SQLModel):
    emision: datetime = Field(default=datetime.now(), sa_type=TIMESTAMP)
    total: int = Field(default=0, nullable=False)
    reserva_id: Optional[UUID] = Field(default=None, foreign_key="reserva.id")
    
class Boleta(BoletaBase, table=True):
    __tablename__ = "boleta"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    reserva: Optional[Reserva] = Relationship(back_populates="boleta")
    
## Modelo de valoracion
class ValoracionBase(SQLModel):
    fecha: datetime = Field(default=datetime.now(), sa_type=TIMESTAMP)
    puntaje: int = Field(default=0, nullable=False)
    comentario: Optional[str] = Field(default=None, nullable=True, sa_type=TEXT)
    cliente_id: Optional[UUID] = Field(default=None, foreign_key="usuario.id")
    propiedad_id: Optional[UUID] = Field(default=None, foreign_key="propiedad.id")
    
class Valoracion(ValoracionBase, table=True):
    __tablename__ = "valoracion"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    cliente: Optional[Usuario] = Relationship(back_populates="valoraciones", sa_relationship={"lazy": "selectin"})
    propiedad: Optional[Propiedad] = Relationship(back_populates="valoraciones", sa_relationship_kwargs={"lazy": "selectin"})
    
