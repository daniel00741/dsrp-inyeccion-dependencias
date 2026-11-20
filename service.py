from dataclasses import dataclass
from typing import Literal

PALABRAS_POSITIVAS = ("excelente", "bueno", "buena", "me encanta", "recomiendo", "rápido", "perfecto")
PALABRAS_NEGATIVAS = ("malo", "mala", "pésimo", "horrible", "no funciona", "lento", "roto", "devolver")


@dataclass(frozen=True)
class Analisis:
    """Resultado del análisis de sentimiento de un texto."""
    sentimiento: Literal["positivo", "negativo", "neutro"]
    positivas: int
    negativas: int


def analizar_sentimiento(texto: str) -> Analisis:
    """Cuenta palabras positivas y negativas y decide el sentimiento."""
    texto = texto.lower()
    positivas = sum(1 for palabra in PALABRAS_POSITIVAS if palabra in texto)
    negativas = sum(1 for palabra in PALABRAS_NEGATIVAS if palabra in texto)

    if positivas > negativas:
        sentimiento = "positivo"
    elif negativas > positivas:
        sentimiento = "negativo"
    else:
        sentimiento = "neutro"

    return Analisis(sentimiento=sentimiento, positivas=positivas, negativas=negativas)