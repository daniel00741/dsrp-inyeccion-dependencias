import json
import logging
import os

from fastapi import Depends, FastAPI

from schemas import ResenaIn, ResultadoOut
from service import Analizador, obtener_analizador

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Analizador de Reseñas", version="0.0.2")

ARCHIVO = "resenas.json"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analizar", response_model=ResultadoOut)
def analizar(
    resena: ResenaIn,
    analizador: Analizador = Depends(obtener_analizador),
) -> ResultadoOut:
    logger.info(f"Reseña de {resena.cliente}: {resena.texto}")

    # --- analizar (con el analizador que nos INYECTARON) ---
    analisis = analizador.analizar(resena.texto)

    # --- guardar ---
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            resenas = json.load(f)
    else:
        resenas = []

    registro = {
        "id": len(resenas) + 1,
        "cliente": resena.cliente,
        "producto": resena.producto,
        "texto": resena.texto,
        "estrellas": resena.estrellas,
        "sentimiento": analisis.sentimiento,
    }
    resenas.append(registro)

    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(resenas, f, ensure_ascii=False, indent=2)

    # --- responder ---
    return ResultadoOut(
        id=registro["id"],
        sentimiento=analisis.sentimiento,
        positivas=analisis.positivas,
        negativas=analisis.negativas,
    )


@app.get("/resenas")
def listar():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    return []