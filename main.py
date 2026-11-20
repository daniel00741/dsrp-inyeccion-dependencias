import json
import logging
import os

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Analizador de Reseñas", version="0.0.1")

ARCHIVO = "resenas.json"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analizar")
def analizar(data: dict):
    # --- validar ---
    if "cliente" not in data or "producto" not in data or "texto" not in data:
        return {"error": "faltan campos"}
    if len(data["texto"]) < 5:
        return {"error": "el texto es muy corto"}
    if "estrellas" in data:
        if data["estrellas"] < 1 or data["estrellas"] > 5:
            return {"error": "estrellas debe estar entre 1 y 5"}

    logger.info(f"Reseña de {data['cliente']}: {data['texto']}")

    # --- analizar ---
    texto = data["texto"].lower()
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

    resena = {
        "id": len(resenas) + 1,
        "cliente": data["cliente"],
        "producto": data["producto"],
        "texto": data["texto"],
        "estrellas": data.get("estrellas"),
        "sentimiento": sentimiento,
    }
    resenas.append(resena)

    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(resenas, f, ensure_ascii=False, indent=2)

    # --- responder ---
    return {
        "id": resena["id"],
        "sentimiento": sentimiento,
        "positivas": positivas,
        "negativas": negativas,
    }


@app.get("/resenas")
def listar():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
