from __future__ import annotations
import io
from PIL import Image
import pypdfium2 as pdfium

# Supported image MIME types
SUPPORTED_IMAGE_TYPES = {
    "image/png", "image/jpeg", "image/jpg", "image/gif", 
    "image/webp", "image/tiff", "image/bmp"
}

def normalize_to_png_bytes(file_bytes: bytes, content_type: str) -> bytes:
    """
    Returns a single PNG image bytes for the first page.
    - If PDF: renders page 1 to an image.
    - If image: converts to PNG.
    
    Raises ValueError for unsupported file types.
    """
    # Check for PDF
    if content_type == "application/pdf" or file_bytes[:4] == b"%PDF":
        try:
            pdf = pdfium.PdfDocument(file_bytes)
            page = pdf.get_page(0)
            pil_image = page.render(scale=2.0).to_pil()
            page.close()
            pdf.close()
            return pil_to_png_bytes(pil_image)
        except Exception as e:
            raise ValueError(f"Failed to process PDF: {str(e)}")

    # Check for supported image types
    if content_type and content_type.startswith("image/"):
        try:
            img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
            return pil_to_png_bytes(img)
        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")
    
    # Try to open as image anyway (for cases where content_type is wrong)
    try:
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        return pil_to_png_bytes(img)
    except Exception:
        raise ValueError(
            f"Unsupported file type: {content_type}. "
            "Please upload a PDF or image file (PNG, JPEG, GIF, WEBP, TIFF, BMP)."
        )

def pil_to_png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
