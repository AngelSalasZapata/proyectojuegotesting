import json
import os

from settings import BASE_DIR


def load_track_config(json_path):
    """Lee un archivo de configuracion de pista (ver tracks/track1.json) y
    devuelve un dict listo para construir un Track con Track.from_config().

    Las rutas 'image' y 'mask' del json son relativas a la raiz del
    proyecto (donde vive settings.py); aqui se convierten a rutas
    absolutas para que pygame pueda cargarlas sin importar desde donde se
    ejecute el juego.
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(
            f"No se encontro el archivo de configuracion de pista: {json_path}"
        )

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for key in ("image", "mask", "road_width", "waypoints"):
        if key not in data:
            raise ValueError(f"Falta la clave '{key}' en {json_path}")

    data["image"] = os.path.join(BASE_DIR, data["image"])
    data["mask"] = os.path.join(BASE_DIR, data["mask"])
    data["waypoints"] = [tuple(point) for point in data["waypoints"]]

    return data