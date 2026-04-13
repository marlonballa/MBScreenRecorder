import json
from pathlib import Path


CONFIG_PATH = Path.home() / "Logs do Sistema" / ".cfg"


def get_config_dir() -> Path:
    path = Path.home() / "Logs do Sistema"
    path.mkdir(exist_ok=True)
    return path


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except Exception:
            pass
    return {"output_dir": str(get_config_dir())}


def save_config(config: dict):
    CONFIG_PATH.write_text(json.dumps(config))