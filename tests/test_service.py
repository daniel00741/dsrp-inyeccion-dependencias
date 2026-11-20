import pytest

from service import analizar_sentimiento


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