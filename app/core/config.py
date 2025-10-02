import os
from pathlib import Path


APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")


def _detect_model_path() -> str:
    candidates = [
        os.getenv("MODEL_PATH"),
        "meanCT_model.keras",
        "meanCT_model.h5",
        str(Path.cwd() / "meanCT_model.keras"),
        str(Path.cwd() / "meanCT_model.h5"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate).resolve())
    # Возвращаем дефолтное имя (может не существовать до деплоя)
    return "meanCT_model.keras"


MODEL_PATH: str = _detect_model_path()
TMP_ROOT: str | None = os.getenv("TMP_ROOT")
ALLOW_RAR: bool = os.getenv("ALLOW_RAR", "true").lower() not in {"0", "false", "no"}


