"""
OCR Processor Module
====================
Handles image preprocessing and text extraction using Tesseract OCR.
Optimized for MCQ text recognition with preprocessing pipeline.
"""

import pytesseract
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import cv2
import numpy as np
import re
import os
import sys
from typing import Optional
from functools import lru_cache


class OCRProcessor:
    """
    Processes images and extracts text using Tesseract OCR.
    Includes preprocessing optimizations for better accuracy.
    """

    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Initialize the OCR processor.

        Args:
            tesseract_path: Custom path to Tesseract executable
        """
        self._configure_tesseract(tesseract_path)

        # Tesseract config for fast, accurate text extraction
        # PSM 6 = Assume a single uniform block of text
        # OEM 3 = Default, based on what is available
        self.tesseract_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789().,-:;?!\' '

    def _configure_tesseract(self, custom_path: Optional[str] = None):
        """
        Configure Tesseract executable path.

        Args:
            custom_path: Custom path to tesseract.exe
        """
        # Common Tesseract installation paths on Windows
        possible_paths = [
            custom_path,
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(os.getenv("USERNAME", "")),
            # For PyInstaller bundled app
            os.path.join(getattr(sys, '_MEIPASS', ''), 'tesseract', 'tesseract.exe'),
        ]

        for path in possible_paths:
            if path and os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return

        # If not found, assume it's in PATH
        # This will raise an error later if Tesseract is not installed

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy.
        Applies grayscale, contrast enhancement, and thresholding.

        Args:
            image: PIL Image to preprocess

        Returns:
            Preprocessed PIL Image
        """
        # Convert PIL to OpenCV format
        img_array = np.array(image)

        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array

        # Apply slight blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (1, 1), 0)

        # Increase contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(blurred)

        # Apply adaptive thresholding for better text visibility
        # Using Otsu's method for automatic threshold selection
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Invert if background is darker than text
        if np.mean(binary) < 127:
            binary = cv2.bitwise_not(binary)

        # Scale up small images for better OCR
        height, width = binary.shape
        if width < 300 or height < 50:
            scale_factor = max(300 / width, 50 / height, 2)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            binary = cv2.resize(binary, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

        # Convert back to PIL
        return Image.fromarray(binary)

    def extract_text(self, image: Image.Image, preprocess: bool = True) -> str:
        """
        Extract text from image using Tesseract OCR.

        Args:
            image: PIL Image to process
            preprocess: Whether to apply preprocessing

        Returns:
            Extracted text string
        """
        try:
            # Preprocess if enabled
            if preprocess:
                processed_image = self.preprocess_image(image)
            else:
                processed_image = image

            # Extract text using Tesseract
            text = pytesseract.image_to_string(
                processed_image,
                config=self.tesseract_config
            )

            return text.strip()

        except Exception as e:
            print(f"OCR extraction error: {e}")
            return ""

    def clean_mcq_text(self, text: str) -> str:
        """
        Clean and format extracted text for MCQ processing.
        Preserves question structure while removing noise.

        Args:
            text: Raw OCR text

        Returns:
            Cleaned and formatted text
        """
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Fix common OCR errors
        replacements = {
            '|': 'I',
            '0': 'O',  # Only in specific contexts
            '1': 'l',  # Only in specific contexts
            '—': '-',
            '–': '-',
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
        }

        # Fix option markers (A), (B), (C), (D) or A., B., C., D.
        text = re.sub(r'\(?\s*([AaBbCcDd])\s*[).]', r'(\1)', text)

        # Normalize option markers to uppercase
        def normalize_option(match):
            return f"({match.group(1).upper()})"

        text = re.sub(r'\(([AaBbCcDd])\)', normalize_option, text)

        # Add newlines before options for better readability
        text = re.sub(r'\s*\(([ABCD])\)', r'\n(\1)', text)

        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)

        return text

    def process_image(self, image: Image.Image) -> str:
        """
        Full processing pipeline: extract and clean text from image.

        Args:
            image: PIL Image containing MCQ

        Returns:
            Cleaned MCQ text ready for AI processing
        """
        raw_text = self.extract_text(image)
        cleaned_text = self.clean_mcq_text(raw_text)
        return cleaned_text


# Singleton instance
_ocr_instance: Optional[OCRProcessor] = None


def get_ocr_processor(tesseract_path: Optional[str] = None) -> OCRProcessor:
    """
    Get or create the singleton OCRProcessor instance.

    Args:
        tesseract_path: Optional custom Tesseract path

    Returns:
        OCRProcessor instance
    """
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = OCRProcessor(tesseract_path)
    return _ocr_instance
