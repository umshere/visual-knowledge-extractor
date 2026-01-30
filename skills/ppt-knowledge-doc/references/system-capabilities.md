# System capabilities (macOS)

Recommended installs:

```bash
brew install tesseract poppler
brew install --cask libreoffice
```

What they do:
- `tesseract`: OCR text inside slide images (screenshots, flowcharts)
- `soffice` (LibreOffice): convert PPT/PPTX to PDF/images when extraction is tricky
- `pdftoppm` (Poppler): convert PDF pages to images for OCR/vision

Quick checks:

```bash
tesseract --version
soffice --version
pdftoppm -h | head
```
