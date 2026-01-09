from pathlib import Path
import json
from rapidfuzz import process, fuzz


DEFAULT_KEYS = [
    "city", "latitude", "longitude", "country", "iso2", "iso3", "admin_name", "complete_city_name"
]

JSON_PATH = r"src/adapters/outbound/weather/cities_info.json"

class CitiesInfoAdapter:
    def __init__(self):
        self._records, self._names = None, None
        self._iniciated = False

    def is_iniciated(self) -> bool:
        return bool(self._iniciated)

    def find_best_city(
            self,
            user_input: str,
            *,
            min_score: int = 75,
            scorer=fuzz.WRatio
        ) -> dict | None:
        
        if not self.is_iniciated(): # Lazy initialization
            self._records, self._names = self.__load_cities_json__()
            self._iniciated = True

        if not isinstance(user_input, str) or not user_input.strip():
            raise ValueError("user_input debe ser un string no vacío.")

        query = user_input.strip()

        match = process.extractOne(query, self._names, scorer=scorer)
        if not match:
            return None

        matched_name, score, idx = match
        if score < min_score:
            return None

        return self._records[idx]


    def __load_cities_json__(self):
        p = Path(JSON_PATH).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"No existe el archivo: {p}")

        with p.open("r", encoding="utf-8") as f:
            records = json.load(f)

        if not isinstance(records, list):
            raise ValueError("El JSON debe ser una LISTA de objetos (records).")

        # Filtra/normaliza records inválidos
        clean_records = []
        names = []
        for r in records:
            if not isinstance(r, dict):
                continue
            name = r.get("complete_city_name")
            if isinstance(name, str) and name.strip():
                clean_records.append(r)
                names.append(name.strip())

        if not clean_records:
            raise ValueError("No encontré registros válidos con 'complete_city_name'.")

        return clean_records, names