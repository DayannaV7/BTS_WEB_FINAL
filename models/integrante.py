from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel, Field
from typing import Optional


class IntegranteBase(SQLModel):
    nombre:      str   = Field(min_length=1, max_length=64)
    edad:        int   = Field(gt=0, lt=120)
    altura:      float = Field(gt=0.0, lt=3.0, description="En metros, ej: 1.81")
    rol:         str   = Field(min_length=2, max_length=128, description="Ej: Líder / Rapper Principal")
    descripcion: Optional[str] = Field(default=None, max_length=500)


class Integrante(IntegranteBase, table=True):
    id:         int | None = Field(default=None, primary_key=True)
    imagen_url: str | None = None
    estado:     str        = Field(default="activo")


class IntegranteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:          int
    nombre:      str
    edad:        int
    altura:      float
    rol:         str
    descripcion: str | None
    imagen_url:  str | None
    estado:      str


class IntegranteUpdate(SQLModel):
    nombre:      str | None   = Field(default=None, min_length=1, max_length=64)
    edad:        int | None   = Field(default=None, gt=0, lt=120)
    altura:      float | None = Field(default=None, gt=0.0, lt=3.0)
    rol:         str | None   = Field(default=None, min_length=2, max_length=128)
    descripcion: str | None   = Field(default=None, max_length=500)
