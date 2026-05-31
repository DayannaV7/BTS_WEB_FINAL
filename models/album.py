from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel, Field
from typing import Optional


class AlbumBase(SQLModel):
    nombre:       str = Field(min_length=1, max_length=128)
    num_canciones: int = Field(gt=0)
    anio:         int = Field(gt=1990, lt=2030, description="Año de lanzamiento")
    descripcion:  Optional[str] = Field(default=None, max_length=500)


class Album(AlbumBase, table=True):
    id:         int | None = Field(default=None, primary_key=True)
    imagen_url: str | None = None
    estado:     str        = Field(default="activo")


class AlbumRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:            int
    nombre:        str
    num_canciones: int
    anio:          int
    descripcion:   str | None
    imagen_url:    str | None
    estado:        str


class AlbumUpdate(SQLModel):
    nombre:        str | None = Field(default=None, min_length=1, max_length=128)
    num_canciones: int | None = Field(default=None, gt=0)
    anio:          int | None = Field(default=None, gt=1990, lt=2030)
    descripcion:   str | None = Field(default=None, max_length=500)
