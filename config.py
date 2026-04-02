"""
Configuration Module
====================
Centralized configuration for MCQ Screen Assistant (Ollama Edition).
Edit this file to customize the application behavior.

NO API KEY NEEDED - Runs free with Ollama!
"""

import os
from typing import Optional


class Config:
    """
    Application configuration.
    Modify these values to customize behavior.
    """

    # =========================================================================
    # HOTKEYS
    # =========================================================================
    # Activation hotkey - press this to start region selection
    HOTKEY: str = "ctrl+shift+x"

    # Exit hotkey - press this to quit the application
    EXIT_HOTKEY: str = "ctrl+shift+q"

    # =========================================================================
    # OLLAMA CONFIGURATION (Local AI - FREE!)
    # =========================================================================
    # Ollama server URL (default: http://localhost:11434)
    OLLAMA_URL: str = "http://localhost:11434"

    # Ollama model to use
    # Fast models (recommended):
    #   - "mistral": Fast & good accuracy ⚡ (DEFAULT)
    #   - "llama2": Fast & good accuracy ⚡
    #   - "neural-chat": Fast & good accuracy ⚡
    #   - "orca-mini": Very fast for weak PCs ⚡⚡
    #
    # Better accuracy (slower):
    #   - "mistral-large": Better accuracy but slower
    #   - "llama2-large": Better accuracy but slower
    OLLAMA_MODEL: str = "mistral"

    # =========================================================================
    # OCR CONFIGURATION
    # =========================================================================
    # Custom Tesseract executable path
    # Set to None to use auto-detection
    TESSERACT_PATH: Optional[str] = None

    # OCR preprocessing options
    OCR_PREPROCESS: bool = True  # Enable image preprocessing
    OCR_SCALE_FACTOR: float = 2.0  # Scale small images for better OCR

    # =========================================================================
    # UI CONFIGURATION
    # =========================================================================
    # Popup display duration (milliseconds)
    POPUP_DURATION_MS: int = 3000

    # Popup fade animation duration (milliseconds)
    FADE_DURATION_MS: int = 200

    # Popup colors (RGBA)
    POPUP_BG_COLOR: tuple = (30, 30, 35, 240)
    ANSWER_COLOR: str = "#4ade80"  # Green
    ERROR_COLOR: str = "#ff6b6b"  # Red
    TEXT_COLOR: str = "rgba(255, 255, 255, 0.85)"

    # =========================================================================
    # CACHE CONFIGURATION
    # =========================================================================
    # Enable response caching (helps with repeated MCQs)
    ENABLE_CACHE: bool = True

    # Maximum cached responses
    CACHE_MAX_SIZE: int = 100

    # =========================================================================
    # ADVANCED
    # =========================================================================
    # Minimum selection size (pixels)
    MIN_SELECTION_SIZE: int = 10

    # Enable debug logging
    DEBUG: bool = False

    @classmethod
    def validate(cls) -> list:
        """
        Validate configuration.
        Returns list of error messages (empty if valid).
        """
        errors = []

        if cls.POPUP_DURATION_MS < 1000:
            errors.append("Popup duration should be at least 1000ms")

        return errors

