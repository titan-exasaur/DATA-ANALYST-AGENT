from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml


CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "config.yaml"


@lru_cache
def load_config() -> Dict[str, Any]:
    """
    Loads application configuration from config/config.yaml.
    Cached so the YAML file is not read repeatedly.
    """

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found at: {CONFIG_PATH}")

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if not config:
        raise ValueError("Config file is empty")

    return config