from __future__ import annotations

import threading
from typing import Optional

try:  # Keras 3 (если есть)
    from keras.models import load_model as _load_model
except Exception:  # fallback для Windows/TF<=2.10
    from tensorflow.keras.models import load_model as _load_model  # type: ignore
import tensorflow as tf

from app.core.config import MODEL_PATH
from app.logger import get_logger


_logger = get_logger(__name__)
_model_lock = threading.Lock()
_model = None  # lazy
_device_label = "CPU"


def _init_device() -> None:
    global _device_label
    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            _device_label = "GPU"
            _logger.info("TensorFlow device: GPU detected (%d)", len(gpus))
        except Exception as e:  # noqa: BLE001
            _device_label = "CPU"
            _logger.warning("GPU present but memory growth setup failed, falling back to CPU: %s", e)
    else:
        _device_label = "CPU"
        _logger.info("TensorFlow device: CPU")


_init_device()


def get_device_label() -> str:
    return _device_label


def get_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                _logger.info("Loading model from %s", MODEL_PATH)
                _model = _load_model(MODEL_PATH)
    return _model


