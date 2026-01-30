from __future__ import annotations

from typing import Optional


def ocr_image_bytes_safe(image_bytes: bytes) -> str:
    """Best-effort OCR. Returns empty string if OCR isn't available."""
    try:
        import pytesseract
        from PIL import Image
        import io

        img = Image.open(io.BytesIO(image_bytes))
        # Basic normalization helps screenshots a bit.
        img = img.convert("RGB")
        txt = pytesseract.image_to_string(img)
        return (txt or "").strip()
    except Exception:
        return ""
