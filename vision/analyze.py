#!/usr/bin/env python3
"""ARIA Vision — Screenshot capture + OCR/Cloud analysis."""
import os
import sys

try:
    import pytesseract
    from PIL import Image
    _HAS_OCR = True
except ImportError:
    _HAS_OCR = False

def analyze_image_local(image_path):
    """Extract text from image using Tesseract OCR."""
    if not _HAS_OCR:
        return "ERROR: pytesseract or Pillow not installed."
    if not os.path.exists(image_path):
        return f"ERROR: Image not found: {image_path}"
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        result = text.strip()
        return result if result else "(No text detected in image)"
    except Exception as e:
        return f"Local OCR failed: {e}"

def analyze_image_cloud(image_path):
    """Send image to Antigravity multimodal API for deep analysis."""
    if not os.path.exists(image_path):
        return f"ERROR: Image not found: {image_path}"
    # Stub: will use Gemini Vision API when keys are provided
    print(f"[VISION] Sending {image_path} to Antigravity Multimodal API...")
    return "Antigravity Cloud Analysis: (Waiting for API Key)"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze.py <image_path> [--cloud]")
        sys.exit(1)

    img = sys.argv[1]
    if "--cloud" in sys.argv:
        print(analyze_image_cloud(img))
    else:
        print(analyze_image_local(img))
