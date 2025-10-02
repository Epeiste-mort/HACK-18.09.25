"""Упрощённый pipeline для немедленного запуска"""
import base64
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import pydicom as pdc
from fastapi import UploadFile
from PIL import Image

from app.logger import get_logger
from app.schemas import AnalyzeResponse
from app.services.model import get_model, get_device_label

_logger = get_logger(__name__)


def _read_dicom_from_zip(zip_path: str) -> list:
    """Прямое чтение DICOM файлов из архива"""
    slices = []
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(tmpdir)
        
        # Найти все файлы
        for root, dirs, files in os.walk(tmpdir):
            for fname in files:
                fpath = os.path.join(root, fname)
                if os.path.getsize(fpath) > 0:
                    try:
                        dc = pdc.dcmread(fpath, force=True)
                        slices.append(dc.pixel_array)
                    except Exception:
                        pass
    return slices


async def simple_process_upload(file: UploadFile) -> AnalyzeResponse:
    """Упрощённый pipeline"""
    work_dir = tempfile.mkdtemp(prefix="work_")
    saved_path = None
    
    try:
        # Сохранить файл
        saved_path = os.path.join(work_dir, file.filename or "upload.zip")
        with open(saved_path, "wb") as f:
            f.write(file.file.read())
        
        _logger.info(f"Processing {saved_path}")
        
        # Прочитать срезы
        slices = _read_dicom_from_zip(saved_path)
        _logger.info(f"Read {len(slices)} slices")
        
        if len(slices) == 0:
            raise ValueError("No DICOM slices found")
        
        # Нормализация
        imgs_np = np.array(slices, dtype=np.float32)
        max_val = np.max(np.abs(imgs_np))
        if max_val > 0:
            imgs_np /= max_val
        
        # Средний срез
        mid_idx = len(imgs_np) // 2
        mean_slice = imgs_np[mid_idx, :, :]
        
        # Resize к 512x512
        if mean_slice.shape != (512, 512):
            pil_img = Image.fromarray((mean_slice * 255).astype(np.uint8))
            pil_img = pil_img.resize((512, 512), Image.BILINEAR)
            mean_slice = np.array(pil_img, dtype=np.float32) / 255.0
        
        # К формату модели (1, 512, 512, 1)
        model_input = mean_slice[np.newaxis, ..., np.newaxis].astype(np.float32)
        
        # Инференс
        model = get_model()
        predictions = model.predict(x=model_input, verbose=0)
        normal, pathology = float(predictions[0, 0]), float(predictions[0, 1])
        label = "Норма" if normal >= pathology else "Патология"
        
        # Превью
        pil_prev = Image.fromarray((mean_slice * 255).astype(np.uint8))
        tmp_png = os.path.join(work_dir, "preview.png")
        pil_prev.save(tmp_png, format="PNG")
        with open(tmp_png, "rb") as f:
            preview_b64 = base64.b64encode(f.read()).decode("ascii")
        
        return AnalyzeResponse(
            label=label,
            probabilities=[normal, pathology],
            device=get_device_label(),
            preview_png_b64=preview_b64,
        )
    finally:
        if Path(work_dir).exists():
            shutil.rmtree(work_dir, ignore_errors=True)

