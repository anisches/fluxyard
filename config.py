import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".fluxyard"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULTS: dict = {
    "model": "qwen-a3b-32k:latest",
    "ollama_host": "http://localhost:11434",
    "ollama_api_key": None,
}


class Config:
    def __init__(self):
        self.data = self._load()

    def _load(self) -> dict:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                saved = json.load(f)
            return {**DEFAULTS, **saved}
        return dict(DEFAULTS)

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    @property
    def model(self) -> str:
        return self.data["model"]

    @model.setter
    def model(self, value: str):
        self.data["model"] = value
        self.save()

    @property
    def ollama_host(self) -> str:
        return self.data.get("ollama_host") or "http://localhost:11434"

    @property
    def ollama_api_key(self) -> str | None:
        return self.data.get("ollama_api_key") or None

    def set(self, key: str, value: str):
        self.data[key] = value
        self.save()

    def get(self, key: str):
        return self.data.get(key)


