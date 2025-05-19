from sqlmodel import SQLModel, Field, Relationship
import uuid
from typing import Optional
from uuid import UUID
from datetime import date

class AutorBase(SQLModel):
    nombre: str = Field(max_length=100, nullable=False)
    apellido: str = Field(max_length=100, nullable=False)
    nacimiento: date = Field(default=None)
    
class Autor(AutorBase, table=True):
    __tablename__ = "autor"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    libros: list["Libro"] = Relationship(back_populates="autor")
    
class LibroBase(SQLModel):
    titulo: str = Field(max_length=100, nullable=False)
    fecha_publicacion: date = Field(default=None)
    autor_id: Optional[UUID] = Field(default=None, foreign_key="autor.id")
    
class Libro(LibroBase, table=True):
    __tablename__ = "libro"
    id: Optional[UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    autor: Optional[Autor] = Relationship(back_populates="libros")