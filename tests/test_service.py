import pytest

from service import analizar_sentimiento, AnalizadorPalabras, obtener_analizador


@pytest.mark.parametrize("texto, sentimiento, positivas, negativas", [
    ("Excelente sonido, lo recomiendo",      "positivo", 2, 0),
    ("Llegó roto, horrible",                 "negativo", 0, 2),
    ("Llegó el martes",                      "neutro",   0, 0),
    ("Bueno pero lento",                     "neutro",   1, 1),
    ("EXCELENTE, PERFECTO",                  "positivo", 2, 0),
])
def test_analizar_sentimiento(texto: str, sentimiento: str, positivas: int, negativas: int) -> None:
    analisis = analizar_sentimiento(texto)
    assert analisis.sentimiento == sentimiento
    assert analisis.positivas == positivas
    assert analisis.negativas == negativas


def test_no_toca_el_disco(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    analizar_sentimiento("Excelente producto")
    assert list(tmp_path.iterdir()) == []

# ---------- paso 4: interfaz, implementación y fábrica ----------

def test_analizador_palabras_da_lo_mismo_que_la_funcion() -> None:
    texto = "Excelente sonido, lo recomiendo"
    assert AnalizadorPalabras().analizar(texto) == analizar_sentimiento(texto)


def test_fabrica_entrega_el_analizador_de_palabras() -> None:
    assert isinstance(obtener_analizador(), AnalizadorPalabras)