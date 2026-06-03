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
    print("[INFO] Running on Windows. Using Poppler from:", POPPLER_PATH)
    print("[INFO] Running on Windows. Using Tesseract from:", pytesseract.pytesseract.tesseract_cmd)
else:
    print("[INFO] Running on Linux/Docker. Relying on system package paths.")

# =========================================================
# 📄 OCR FUNCTION
# =========================================================

def extract_text(pdf_path: str) -> str:
    """
    Extract text from a PDF file using a hybrid strategy:
    1. Try digital text extraction via pypdf (fast and low-memory).
    2. Fall back to Poppler + Tesseract OCR if the PDF is scanned.
    """

    print("[OCR] Started text extraction for:", pdf_path)

    # Safety checks
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # 1. Try digital text extraction first
    try:
        import pypdf
        print("[OCR] Attempting digital text extraction via pypdf...")
        reader = pypdf.PdfReader(pdf_path)
        digital_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                digital_text += page_text + "\n"
        
        if len(digital_text.strip()) > 100:
            print(f"[OCR] Digital text extraction succeeded. Extracted {len(digital_text)} characters.")
            return digital_text
        else:
            print("[OCR] Digital text extraction returned insufficient content. Falling back to OCR...")
    except Exception as e:
        print(f"[OCR] Digital text extraction failed: {e}. Falling back to OCR...")

    # 2. Fall back to Poppler + Tesseract OCR
    # Only run path checks if on Windows
    if IS_WINDOWS:
        if not POPPLER_PATH or not os.path.exists(POPPLER_PATH):
            raise FileNotFoundError(f"Poppler path not found: {POPPLER_PATH}")

        if not os.path.exists(pytesseract.pytesseract.tesseract_cmd):
            raise FileNotFoundError(
                f"Tesseract not found: {pytesseract.pytesseract.tesseract_cmd}"
            )

    from pdf2image import pdfinfo_from_path
    from pdf2image import convert_from_path

    # Get total page count
    if IS_WINDOWS:
        info = pdfinfo_from_path(pdf_path, poppler_path=POPPLER_PATH)
    else:
        info = pdfinfo_from_path(pdf_path)
        
    total_pages = info.get("Pages", 1)
    print(f"[OCR] Total pages detected: {total_pages}")

    full_text = ""

    for idx in range(1, total_pages + 1):
        print(f"[OCR] Processing page {idx}/{total_pages}...")
        # Convert only one page at a time with a safe 150 DPI to save memory
        if IS_WINDOWS:
            pages = convert_from_path(pdf_path, dpi=150, first_page=idx, last_page=idx, poppler_path=POPPLER_PATH)
        else:
            pages = convert_from_path(pdf_path, dpi=150, first_page=idx, last_page=idx)
            
        if pages:
            text = pytesseract.image_to_string(pages[0])
            full_text += text + "\n"
            pages[0].close()

    print("[OCR] Completed successfully.")
    return full_text
