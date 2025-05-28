from datetime import datetime
from typing import Optional
from uuid import UUID
import uuid
from sqlmodel import TEXT, TIMESTAMP, Field, Relationship, SQLModel
from models.PropiedadModel import Propiedad
from models.UsuarioModel import Usuario

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
    