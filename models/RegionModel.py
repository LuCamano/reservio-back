from sqlmodel import SQLModel, Field


## Modelo de Region
class RegionBase(SQLModel):
    nombre: str = Field(max_length=100, nullable=False, unique=True)
