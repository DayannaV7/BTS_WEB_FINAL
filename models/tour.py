from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel, Field
from typing import Optional


class TourBase(SQLModel):
    nombre:            str = Field(min_length=1, max_length=128)
    ciudades_visitadas: str = Field(min_length=1, description="Ciudades separadas por coma")
    anio:              int = Field(gt=1990, lt=2030)
    album_id:          int = Field(gt=0, foreign_key="album.id",
                                   description="ID del álbum que promociona este tour")


class Tour(TourBase, table=True):
    id:     int | None = Field(default=None, primary_key=True)
    estado: str        = Field(default="activo")


class TourRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:                int
    nombre:            str
    ciudades_visitadas: str
    anio:              int
    album_id:          int
    estado:            str


class TourUpdate(SQLModel):
    nombre:            str | None = Field(default=None, min_length=1, max_length=128)
    ciudades_visitadas: str | None = None
    anio:              int | None = Field(default=None, gt=1990, lt=2030)
