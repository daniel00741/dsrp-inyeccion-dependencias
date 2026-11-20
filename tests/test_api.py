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


# ---------- validación del contrato (corregido en el paso 2) ----------

@pytest.mark.parametrize("cuerpo, campo, tipo_error", [
    ({"cliente": "Ana Torres", "texto": "Excelente"},
     "producto", "missing"),
    ({"cliente": "Ana Torres", "producto": "X200", "texto": "hola"},
     "texto", "string_too_short"),
    ({"cliente": "Ana Torres", "producto": "X200", "texto": "Muy bueno", "estrellas": 9},
     "estrellas", "less_than_equal"),
    ({"cliente": "Ana Torres", "producto": "X200", "texto": "Muy bueno", "estrellas": "cinco"},
     "estrellas", "int_parsing"),
    ({"cliente": "Ana Torres", "producto": "X200", "texto": 12345},
     "texto", "string_type"),
])
def test_rechaza_datos_invalidos_con_422(cuerpo: dict, campo: str, tipo_error: str) -> None:
    respuesta = client.post("/analizar", json=cuerpo)
    assert respuesta.status_code == 422
    error = respuesta.json()["detail"][0]
    assert error["loc"] == ["body", campo]
    assert error["type"] == tipo_error


def test_dato_invalido_no_se_guarda() -> None:
    client.post("/analizar", json={"cliente": "Ana Torres", "producto": "X200", "texto": "hola"})
    assert client.get("/resenas").json() == []