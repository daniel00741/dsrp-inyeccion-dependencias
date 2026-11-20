import json
import logging
import os

from fastapi import FastAPI

from schemas import ResenaIn, ResultadoOut

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Analizador de Reseñas", version="0.0.2")

ARCHIVO = "resenas.json"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analizar", response_model=ResultadoOut)
def analizar(resena: ResenaIn) -> ResultadoOut:
    # --- validar ---
    # (ya no hace falta: Pydantic valida ANTES de que esta función se ejecute)

    logger.info(f"Reseña de {resena.cliente}: {resena.texto}")

    # --- analizar ---
    texto = resena.texto.lower()
    positivas = 0
    negativas = 0
    for p in ["excelente", "bueno", "buena", "me encanta", "recomiendo", "rápido", "perfecto"]:
        if p in texto:
            positivas = positivas + 1
    for p in ["malo", "mala", "pésimo", "horrible", "no funciona", "lento", "roto", "devolver"]:
        if p in texto:
            negativas = negativas + 1

    if positivas > negativas:
        sentimiento = "positivo"
    elif negativas > positivas:
        sentimiento = "negativo"
    else:
        sentimiento = "neutro"

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
        "sentimiento": sentimiento,
    }
    resenas.append(registro)

    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(resenas, f, ensure_ascii=False, indent=2)

    # --- responder ---
    return ResultadoOut(
        id=registro["id"],
        sentimiento=sentimiento,
        positivas=positivas,
        negativas=negativas,
    )


@app.get("/resenas")
def listar():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    return []