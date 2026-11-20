from dataclasses import dataclass
from typing import Literal, Protocol

PALABRAS_POSITIVAS = ("excelente", "bueno", "buena", "me encanta", "recomiendo", "rápido", "perfecto")
PALABRAS_NEGATIVAS = ("malo", "mala", "pésimo", "horrible", "no funciona", "lento", "roto", "devolver")


@dataclass(frozen=True)
class Analisis:
    """Resultado del análisis de sentimiento de un texto."""
    sentimiento: Literal["positivo", "negativo", "neutro"]
    positivas: int
    negativas: int


# 1. LA PROMESA: cualquier analizador debe tener este método
class Analizador(Protocol):
    def analizar(self, texto: str) -> Analisis: ...


# 2. QUIEN CUMPLE LA PROMESA HOY: palabras clave
class AnalizadorPalabras:
    def analizar(self, texto: str) -> Analisis:
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


# 3. LA FÁBRICA: el ÚNICO lugar que decide qué analizador se usa
def obtener_analizador() -> Analizador:
    """Punto de extensión: aquí se enchufará un analizador con LLM."""
    return AnalizadorPalabras()


# 4. EL PUENTE: mantiene viva la función vieja para que main.py no se entere
def analizar_sentimiento(texto: str) -> Analisis:
    return obtener_analizador().analizar(texto)