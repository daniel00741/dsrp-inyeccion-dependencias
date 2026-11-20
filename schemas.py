from typing import Literal

from pydantic import BaseModel, Field


class ResenaIn(BaseModel):
    """Contrato de ENTRADA: lo que el cliente nos envía."""
    cliente: str = Field(min_length=2, max_length=100)
    producto: str = Field(min_length=2, max_length=100)
    texto: str = Field(min_length=5, max_length=2000)
    estrellas: int | None = Field(default=None, ge=1, le=5)


class ResultadoOut(BaseModel):
    """Contrato de SALIDA: lo que respondemos."""
    id: int
    sentimiento: Literal["positivo", "negativo", "neutro"]
    positivas: int
    negativas: int