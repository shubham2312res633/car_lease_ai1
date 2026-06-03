import os
import sys
from pdf2image import convert_from_path
import pytesseract

# =========================================================
# 🔧 SYSTEM PATH CONFIGURATION (DYNAMIC WINDOWS vs LINUX)
# =========================================================

IS_WINDOWS = sys.platform.startswith('win')

POPPLER_PATH = None
if IS_WINDOWS:
    POPPLER_PATH = r"C:\Users\shubh\OneDrive\Desktop\car_lease_ai\poppler\Library\bin"
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    print("🧰 Running on Windows. Using Poppler from:", POPPLER_PATH)
    print("🔎 Running on Windows. Using Tesseract from:", pytesseract.pytesseract.tesseract_cmd)
else:
    print("🧰 Running on Linux/Docker. Relying on system package paths.")

# =========================================================
# 📄 OCR FUNCTION
# =========================================================

def extract_text(pdf_path: str) -> str:
    """
    Extract text from a PDF file using Poppler + Tesseract OCR
    """

    print("📄 OCR started for:", pdf_path)

    # Safety checks
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"❌ PDF not found: {pdf_path}")

    # Only run path checks if on Windows
    if IS_WINDOWS:
        if not POPPLER_PATH or not os.path.exists(POPPLER_PATH):
            raise FileNotFoundError(f"❌ Poppler path not found: {POPPLER_PATH}")

        if not os.path.exists(pytesseract.pytesseract.tesseract_cmd):
            raise FileNotFoundError(
                f"❌ Tesseract not found: {pytesseract.pytesseract.tesseract_cmd}"
            )

    # Convert PDF → images
    if IS_WINDOWS:
        pages = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    else:
        # On Linux, pdf2image resolves pdftoppm from the system PATH automatically
        pages = convert_from_path(pdf_path)
        
    print(f"🖼️ Total pages detected: {len(pages)}")

    full_text = ""

    for idx, page in enumerate(pages, start=1):
        print(f"🔍 OCR processing page {idx}...")
        text = pytesseract.image_to_string(page)
        full_text += text + "\n"

    print("✅ OCR completed successfully.")
    return full_text
