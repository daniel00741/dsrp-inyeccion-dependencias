import pytest
from fastapi.testclient import TestClient

from main import app

# raise_server_exceptions=False: si la app revienta, queremos ver el 500
# como lo vería un cliente real, en vez de que el test se caiga.
client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def carpeta_temporal(tmp_path, monkeypatch):
    """PARCHE TEMPORAL: cada test corre en una carpeta vacía distinta,
    para que no escriba en tu resenas.json real. Lo eliminaremos en el paso 7."""
    monkeypatch.chdir(tmp_path)


# ---------- casos felices ----------

def test_health() -> None:
    respuesta = client.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}


def test_resena_positiva() -> None:
    respuesta = client.post("/analizar", json={
        "cliente": "Ana Torres", "producto": "X200",
        "texto": "Excelente sonido, lo recomiendo", "estrellas": 5,
    })
    assert respuesta.status_code == 200
    assert respuesta.json() == {"id": 1, "sentimiento": "positivo", "positivas": 2, "negativas": 0}


def test_resena_negativa() -> None:
    respuesta = client.post("/analizar", json={
        "cliente": "Luis Paz", "producto": "X200", "texto": "Llegó roto, horrible",
    })
    assert respuesta.status_code == 200
    assert respuesta.json()["sentimiento"] == "negativo"
    assert respuesta.json()["negativas"] == 2


def test_resena_neutra() -> None:
    respuesta = client.post("/analizar", json={
        "cliente": "Eva Ríos", "producto": "X200", "texto": "Llegó el martes",
    })
    assert respuesta.status_code == 200
    assert respuesta.json()["sentimiento"] == "neutro"


# ---------- guardado ----------

def test_guarda_y_lista_resenas() -> None:
    client.post("/analizar", json={"cliente": "Ana Torres", "producto": "X200", "texto": "Muy bueno"})
    client.post("/analizar", json={"cliente": "Luis Paz", "producto": "X200", "texto": "Muy malo"})

    respuesta = client.get("/resenas")
    assert respuesta.status_code == 200
    assert [r["id"] for r in respuesta.json()] == [1, 2]
    assert [r["sentimiento"] for r in respuesta.json()] == ["positivo", "negativo"]


def test_crea_el_archivo_en_disco(tmp_path) -> None:
    client.post("/analizar", json={"cliente": "Ana Torres", "producto": "X200", "texto": "Muy bueno"})
    assert (tmp_path / "resenas.json").exists()


# ---------- DEFECTOS ACTUALES (cambiarán en el paso 2) ----------

@pytest.mark.parametrize("cuerpo, error", [
    ({"cliente": "Ana Torres", "texto": "Excelente"},                          "faltan campos"),
    ({"cliente": "Ana Torres", "producto": "X200", "texto": "hola"},           "el texto es muy corto"),
    ({"cliente": "Ana Torres", "producto": "X200", "texto": "Muy bueno", "estrellas": 9},
                                                                               "estrellas debe estar entre 1 y 5"),
])
def test_DEFECTO_errores_responden_200(cuerpo: dict, error: str) -> None:
    respuesta = client.post("/analizar", json=cuerpo)
    assert respuesta.status_code == 200          # ← está MAL, pero es lo que hace hoy
    assert respuesta.json() == {"error": error}


def test_DEFECTO_estrellas_como_texto_revienta_con_500() -> None:
    respuesta = client.post("/analizar", json={
        "cliente": "Ana Torres", "producto": "X200", "texto": "Muy bueno", "estrellas": "cinco",
    })
    assert respuesta.status_code == 500          # ← está MAL, pero es lo que hace hoy