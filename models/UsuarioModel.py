from datetime import date
from sqlmodel import SQLModel, Field, Enum
from models.types import UserType

## Modelo de Usuario
class UsuarioBase(SQLModel):
    email: str = Field(max_length=150, nullable=False, unique=True, index=True)
    rut: str = Field(max_length=12, nullable=False, unique=True, index=True)
    nombres: str = Field(max_length=150, nullable=False)
    appaterno: str = Field(max_length=100, nullable=False)
    apmaterno: str = Field(max_length=100, nullable=False)
    fecha_nacimiento: date = Field(nullable=False)
    tipo: UserType = Field(default=UserType.cliente, sa_type=Enum(UserType))
    password: str = Field(max_length=100, nullable=False)

class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenRequest(SQLModel):
    refresh_token: str