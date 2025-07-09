from datetime import datetime, date, time
from typing import List, Optional
from uuid import UUID
import uuid
from sqlmodel import JSON, Column, Field, Relationship, TIMESTAMP, SQLModel, TEXT

from models.types import UserType, PagoStatus, ComisionStatus
from .UsuarioModel import UsuarioBase
from .ComunaModel import ComunaBase
from .RegionModel import RegionBase
from .PropiedadModel import PropiedadBase
from .ReservaModel import ReservaBase
from .BoletaModel import BoletaBase
from .ValoracionModel import ValoracionBase
from .PagoModel import PagoBase
from .ComisionModel import ComisionBase
from .manyToMany import UsuarioPropiedad

# Clases tabla (heredan de su base)
class Usuario(UsuarioBase, table=True):
    __tablename__ = "usuario"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    fecha_creacion: datetime = Field(default=datetime.now(), sa_type=TIMESTAMP)
    propiedades: list["Propiedad"] = Relationship(link_model=UsuarioPropiedad, back_populates="propietarios")
    bloqueos: list["BloqueoUsuario"] = Relationship(back_populates="usuario", sa_relationship_kwargs={"foreign_keys": "BloqueoUsuario.usuario_id"})

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
    documento: Optional[str] = Field(default=None, sa_type=TEXT, nullable=True)
    comuna: Optional[Comuna] = Relationship(back_populates="propiedades")
    propietarios: list["Usuario"] = Relationship(link_model=UsuarioPropiedad, back_populates="propiedades")
    valoraciones: list["Valoracion"] = Relationship(back_populates="propiedad")

class Reserva(ReservaBase, table=True):
    __tablename__ = "reserva"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    fecha_creacion: datetime = Field(default=datetime.now(), sa_type=TIMESTAMP)
    boleta: Optional["Boleta"] = Relationship(back_populates="reserva")
    pagos: list["Pago"] = Relationship(back_populates="reserva")

class Boleta(BoletaBase, table=True):
    __tablename__ = "boleta"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    reserva: Optional[Reserva] = Relationship(back_populates="boleta")

class Valoracion(ValoracionBase, table=True):
    __tablename__ = "valoracion"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    propiedad: Optional[Propiedad] = Relationship(back_populates="valoraciones")
    cliente: Optional[Usuario] = Relationship()

class Pago(PagoBase, table=True):
    __tablename__ = "pago"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    reserva: Optional[Reserva] = Relationship(back_populates="pagos")
    comisiones: list["Comision"] = Relationship(back_populates="pago")

class Comision(ComisionBase, table=True):
    __tablename__ = "comision"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    pago: Optional[Pago] = Relationship(back_populates="comisiones")
    propietario: Optional[Usuario] = Relationship()
    
class BloqueoUsuario(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    motivo: str = Field(sa_type=TEXT, nullable=False)
    fecha_bloqueo: datetime = Field(default=datetime.now(), sa_type=TIMESTAMP)
    fecha_desbloqueo: Optional[datetime] = Field(default=None, sa_type=TIMESTAMP)
    usuario_id: UUID = Field(foreign_key="usuario.id", nullable=False)
    administrador_id: UUID = Field(foreign_key="usuario.id", nullable=False)
    usuario: Optional["Usuario"] = Relationship(back_populates="bloqueos", sa_relationship_kwargs={"foreign_keys": "BloqueoUsuario.usuario_id"})
    administrador: Optional["Usuario"] = Relationship(sa_relationship_kwargs={"foreign_keys": "BloqueoUsuario.administrador_id"})
    
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
    fecha_creacion: datetime
    propiedades: list["Propiedad"] = []
    bloqueos: list["BloqueoUsuario"] = []
    
class PropiedadRead(SQLModel):
    id: UUID
    nombre: Optional[str]
    descripcion: str
    direccion: str
    tipo: str
    cod_postal: str
    capacidad: Optional[int]
    precio_hora: int
    hora_apertura: Optional[time]
    hora_cierre: Optional[time]
    comuna_id: Optional[UUID]
    validada: bool
    activo: bool
    imagenes: Optional[List[str]]
    documento: Optional[str]
    comuna: Optional["Comuna"]
    propietarios: list["Usuario"]
    valoraciones: list["Valoracion"]