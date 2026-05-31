from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class VotoBase(SQLModel):
    nombre_fan:    str = Field(min_length=2, max_length=64,
                               description="Tu nombre o apodo de ARMY")
    integrante_id: int = Field(gt=0, foreign_key="integrante.id",
                               description="ID del integrante favorito")
    comentario:    Optional[str] = Field(default=None, max_length=300,
                                         description="¿Por qué es tu favorito?")


class VotoFan(VotoBase, table=True):
    id:    int | None  = Field(default=None, primary_key=True)
    fecha: datetime    = Field(default_factory=datetime.utcnow)


class VotoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:            int
    nombre_fan:    str
    integrante_id: int
    comentario:    str | None
    fecha:         datetime


class VotoStats(BaseModel):
    """Estadísticas de popularidad para el dashboard."""
    integrante_id:     int
    nombre_integrante: str
    imagen_url:        str | None
    total_votos:       int
    porcentaje:        float
