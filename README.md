# Analizador de Reseñas

Proyecto de práctica para el curso **Fundamentos de Ingeniería de Software e IA** (especialización AI Engineer, DSRP).

Una API pequeña que recibe reseñas de clientes de una tienda online, decide si son **positivas, negativas o neutras** con palabras clave y las guarda en un archivo JSON.

El código parte **con deuda técnica a propósito**. Cada paso del ejercicio la paga con una técnica de ingeniería de software, hasta llegar a un diseño desacoplado con inyección de dependencias.

## Cómo ejecutarlo

```bash
python3 -m venv .venv
source .venv/bin/activate          # en Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

Abre http://127.0.0.1:8000/docs y prueba `POST /analizar` con:

```json
{
  "cliente": "Ana Torres",
  "producto": "Audífonos X200",
  "texto": "Excelente sonido, lo recomiendo",
  "estrellas": 5
}
```

## Paso 0: deudas técnicas de esta versión

| # | Deuda | Dónde | Riesgo |
|---|---|---|---|
| 1 | Un endpoint hace todo: valida, analiza, guarda y responde | `analizar()` | Para probar el análisis hay que levantar la API y escribir en disco |
| 2 | Validación manual con `if` sobre un `dict` | `analizar()` | No valida tipos: `"estrellas": "cinco"` o `"texto": 123` revientan con un 500 |
| 3 | Los errores responden **200** con `{"error": ...}` | `analizar()` | Quien consume la API cree que todo salió bien |
| 4 | Palabras clave escritas dentro del endpoint | `analizar()` | Cambiar una regla obliga a tocar la API |
| 5 | El endpoint lee y escribe el archivo directamente | `analizar()` y `listar()` | Imposible cambiar a una base de datos sin reescribir todo; los tests ensucian el disco |
| 6 | El análisis está amarrado a una sola implementación | `analizar()` | Pasar a un LLM significa reescribir el endpoint |
| 7 | El log registra el nombre del cliente y el texto completo | `logger.info(...)` | Datos personales en los logs |
| 8 | Sin pruebas automatizadas | — | Ningún cambio se puede hacer con seguridad |
| 9 | Dependencias sin versión fija | `requirements.txt` | El proyecto puede romperse solo al reinstalar |

## Plan de refactorización

| Paso | Qué se hace | Concepto |
|---|---|---|
| 0 | Versión con deuda técnica | Identificar la deuda |
| 1 | Tests antes de tocar nada | Tests de caracterización |
| 2 | Contratos con Pydantic | Contratos de datos (el 200 con error pasa a 422) |
| 3 | Lógica a `service.py` | Refactorización, SRP |
| 4 | `Protocol Analizador` + `AnalizadorPalabras` + fábrica | Interfaces, Strategy, Factory (expand) |
| 5 | El endpoint recibe el analizador con `Depends` | Inyección de dependencias (migrate) |
| 6 | Borrar el código viejo | Limpieza (contract) |
| 7 | `Repositorio` con `RepositorioArchivo` y `RepositorioMemoria` | DI de una segunda dependencia, capa de infraestructura |
| 8 | Tests con `dependency_overrides` | Probar sin efectos secundarios |
| 9 | `AnalizadorLLMFalso` enchufado cambiando una línea | Demostración del desacoplamiento |
