"""Konfigurationsverwaltung fuer n8nManager."""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_CONFIG = {
    "api_port": 8100,
    "default_server": None,
    "db_path": "data/n8n_manager.db",
    "bach": {
        "enabled": False,
        "db_path": None,
        "system_path": None,
    },
    "n8n": {
        "default_port": 5678,
        "api_version": "v1",
    },
}


def load_config(config_path=None) -> dict:
    """Laedt JSON-Konfiguration und merged mit Defaults."""
    if config_path is None:
        config_path = BASE_DIR / "config.json"
    config_path = Path(config_path)

    config = _deep_merge({}, DEFAULT_CONFIG)

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
            config = _deep_merge(config, user_config)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[n8nManager] Warnung: config.json konnte nicht geladen werden: {e}")

    return config


def save_config(config: dict, config_path=None):
    """Speichert Konfiguration als JSON."""
    if config_path is None:
        config_path = BASE_DIR / "config.json"
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def get_db_path(config=None) -> Path:
    """Gibt absoluten Pfad zur Datenbank zurueck."""
    if config is None:
        config = load_config()
    db_path = config.get("db_path", DEFAULT_CONFIG["db_path"])
    p = Path(db_path)
    if not p.is_absolute():
        p = BASE_DIR / p
    return p.resolve()


def _deep_merge(base: dict, override: dict) -> dict:
    """Rekursiver Merge: override-Werte ueberschreiben base-Werte."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
