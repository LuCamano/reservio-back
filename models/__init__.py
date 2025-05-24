from sqlmodel import SQLModel, Field, Relationship
import enum
from sqlalchemy.types import Enum
import uuid
from typing import Optional
from uuid import UUID
from datetime import date

class UserType(enum.Enum):
    """ Enumerador para el tipo de usuario """
    admin = "admin"
    cliente = "cliente"
    propietario = "propietario"

# class AutorBase(SQLModel):
#     nombre: str = Field(max_length=100, nullable=False)
#     apellido: str = Field(max_length=100, nullable=False)
#     nacimiento: date = Field(default=None)
    
# class Autor(AutorBase, table=True):
#     __tablename__ = "autor"
#     id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
#     libros: list["Libro"] = Relationship(back_populates="autor")
    
# class LibroBase(SQLModel):
#     titulo: str = Field(max_length=100, nullable=False)
#     fecha_publicacion: date = Field(default=None)
#     autor_id: Optional[UUID] = Field(default=None, foreign_key="autor.id")
    
# class Libro(LibroBase, table=True):
#     __tablename__ = "libro"
#     id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
#     autor: Optional[Autor] = Relationship(back_populates="libros")

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