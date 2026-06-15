import json
import unicodedata
from pathlib import Path

# Ruta a la base de datos de soluciones
BD_PATH = Path(__file__).parent / "base_datos.json"


def normalizar(texto: str) -> str:
    """
    Convierte el texto a minúsculas y elimina tildes/diacríticos.
    Permite que 'conexión' matchee con el keyword 'conexion'.

    Ejemplo:
        normalizar("No tengo Conexión") → "no tengo conexion"
    """
    texto = texto.lower()
    nfkd = unicodedata.normalize("NFD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def cargar_base_datos() -> list[dict]:
    """
    Carga el archivo base_datos.json.
    Retorna lista vacía si el archivo no existe (manejo de error).
    """
    if not BD_PATH.exists():
        print(f"[WARN] No se encontró la base de datos en {BD_PATH}")
        return []
    try:
        with open(BD_PATH, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Error al leer base_datos.json: {e}")
        return []


def clasificar(descripcion: str) -> dict | None:
    """
    Busca la primera solución conocida que coincida con la descripción.

    Implementa el Gateway GW-1 (¿tipo de problema conocido?) y
    GW-2 (¿solución encontrada?) del diagrama BPMN.

    Args:
        descripcion: Texto libre ingresado por el usuario.

    Returns:
        Diccionario con la solución si se encontró, None si no.

    Ejemplos:
        >>> clasificar("no tengo internet")
        {'id': 1, 'categoria': 'Red', ...}

        >>> clasificar("mi compu explota")
        None
    """
    texto_normalizado = normalizar(descripcion)
    base = cargar_base_datos()

    for solucion in base:
        for keyword in solucion.get("keywords", []):
            if keyword in texto_normalizado:
                return solucion

    return None  # → Gateway: "Nuevo / sin solución conocida" → escalar


def listar_categorias() -> list[str]:
    """Devuelve las categorías únicas disponibles en la BD."""
    base = cargar_base_datos()
    return list({s["categoria"] for s in base})


def buscar_por_categoria(categoria: str) -> list[dict]:
    """Filtra soluciones por categoría."""
    base = cargar_base_datos()
    cat_norm = normalizar(categoria)
    return [s for s in base if normalizar(s["categoria"]) == cat_norm]


# ─── Tests rápidos ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    casos = [
        ("no tengo internet",          "Red"),
        ("la impresora no imprime",     "Hardware"),
        ("pantalla negra",              "Hardware"),
        ("la pc va muy lenta",          "Software"),
        ("olvide mi contraseña",        "Software"),
        ("no me llegan los correos",    "Software"),
        ("mi compu explota literalmente", None),
        ("",                            None),
        ("12345",                       None),
    ]

    print("Test de clasificador")
    errores = 0
    for texto, cat_esperada in casos:
        resultado = clasificar(texto)
        cat_obtenida = resultado["categoria"] if resultado else None
        ok = "✓" if cat_obtenida == cat_esperada else "✗"
        if cat_obtenida != cat_esperada:
            errores += 1
        print(f"  {ok}  '{texto[:35]:<35}' → {cat_obtenida or 'None':<12} (esperado: {cat_esperada or 'None'})")

    print(f"\n  Resultado: {len(casos)-errores}/{len(casos)} correctos")
