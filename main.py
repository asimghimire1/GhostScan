"""
MCQ Screen Assistant - Main Application
========================================
A fast, minimal, AI-powered screen assistant for solving MCQs using Ollama (local AI).

Press Ctrl+Shift+X to select a screen region containing an MCQ.
The app will OCR the text, send it to Ollama, and display the answer.

❌ NO API KEY NEEDED - Runs completely free locally!

Author: MCQ Assistant
Version: 2.0.0 (Ollama Edition)
"""

import sys
import os
import threading
import time
from typing import Optional
import keyboard
import requests
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, QObject

# Import our modules
from screen_capture import get_screen_capture
from ocr_processor import get_ocr_processor
from ai_handler import get_ai_handler, MCQAnswer
from ui_overlay import get_ui_manager


# ============================================================================
# Configuration
# ============================================================================

class Config:
    """Application configuration."""
    HOTKEY = "ctrl+shift+x"
    EXIT_HOTKEY = "ctrl+shift+q"
    POPUP_DURATION_MS = 3000

    # Optional: Set custom Tesseract path if not in default location
    TESSERACT_PATH: Optional[str] = None

    # Ollama configuration
    OLLAMA_URL = "http://localhost:11434"  # Default Ollama server URL
    OLLAMA_MODEL = "mistral"  # Fast and free model
    # Other options: "llama2", "neural-chat", "orca-mini"


# ============================================================================
# Worker Thread for Background Processing
# ============================================================================

class ProcessingWorker(QObject):
    """
    Worker for processing MCQ in background thread.
    Emits signals when processing is complete.
    """

    finished = pyqtSignal(object)  # MCQAnswer
    error = pyqtSignal(str)

    def __init__(self, image, ocr_processor, ai_handler):
        super().__init__()
        self.image = image
        self.ocr = ocr_processor
        self.ai = ai_handler

    def process(self):
        """Process the image and get AI answer."""
        try:
            # OCR extraction
            text = self.ocr.process_image(self.image)

            if not text or len(text.strip()) < 10:
                self.error.emit("Could not extract text. Try selecting a clearer region.")
                return

            # AI processing
            answer = self.ai.solve_mcq(text)
            self.finished.emit(answer)

        except Exception as e:
            self.error.emit(f"Processing error: {str(e)}")


# ============================================================================
# Main Application
# ============================================================================

class MCQAssistant:
    """
    Main application class for MCQ Screen Assistant.
    Manages hotkeys, screen capture, OCR, AI calls, and UI.
    """

    def __init__(self):
        """Initialize the MCQ Assistant."""
        self.running = False
        self.processing = False

        # Initialize components
        self.screen_capture = get_screen_capture()
        self.ocr_processor = get_ocr_processor(Config.TESSERACT_PATH)
        self.ai_handler = get_ai_handler(Config.OLLAMA_URL, Config.OLLAMA_MODEL)
        self.ui_manager = get_ui_manager()

        # Processing thread
        self._worker_thread: Optional[QThread] = None
        self._worker: Optional[ProcessingWorker] = None

    def start(self):
        """Start the application."""
        self.running = True

        print("=" * 50)
        print("MCQ Screen Assistant")
        print("=" * 50)
        print(f"Hotkey: {Config.HOTKEY.upper()} - Select region")
        print(f"Exit:   {Config.EXIT_HOTKEY.upper()} - Quit app")
        print("=" * 50)
        print("Running in background... Press the hotkey to start.")
        print()

        # Register global hotkeys
        keyboard.add_hotkey(Config.HOTKEY, self._on_hotkey_pressed, suppress=True)
        keyboard.add_hotkey(Config.EXIT_HOTKEY, self._on_exit_pressed, suppress=True)

        # Ensure Qt app exists
        self.ui_manager.ensure_app()
        app = QApplication.instance()

        # Create a timer to keep the event loop responsive
        keep_alive_timer = QTimer()
        keep_alive_timer.timeout.connect(lambda: None)
        keep_alive_timer.start(100)

        try:
            # Run the Qt event loop
            while self.running:
                app.processEvents()
                time.sleep(0.01)  # Prevent high CPU usage

        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self):
        """Stop the application."""
        self.running = False
        keyboard.unhook_all()
        print("\nMCQ Assistant stopped.")

    def _on_hotkey_pressed(self):
        """Handle hotkey press - start selection."""
        if self.processing:
            return  # Already processing

        # Use QTimer to run in main thread
        QTimer.singleShot(0, self._start_selection)

    def _on_exit_pressed(self):
        """Handle exit hotkey."""
        self.running = False

    def _start_selection(self):
        """Start the screen selection overlay."""
        self.ui_manager.start_selection(
            callback=self._on_selection_complete,
            cancel_callback=self._on_selection_cancelled
        )

    def _on_selection_complete(self, x1: int, y1: int, x2: int, y2: int):
        """Handle completed selection."""
        if self.processing:
            return

        self.processing = True

        # Show loading indicator
        self.ui_manager.show_loading()

        # Capture the selected region
        image = self.screen_capture.capture_region(x1, y1, x2, y2)

        if image is None:
            self.ui_manager.show_error("Failed to capture screen region.")
            self.processing = False
            return

        # Process in background thread
        self._process_image(image)

    def _on_selection_cancelled(self):
        """Handle cancelled selection."""
        pass  # Nothing to do

    def _process_image(self, image):
        """Process the captured image in a background thread."""
        # Create worker and thread
        self._worker_thread = QThread()
        self._worker = ProcessingWorker(image, self.ocr_processor, self.ai_handler)
        self._worker.moveToThread(self._worker_thread)

        # Connect signals
        self._worker_thread.started.connect(self._worker.process)
        self._worker.finished.connect(self._on_processing_complete)
        self._worker.error.connect(self._on_processing_error)
        self._worker.finished.connect(self._cleanup_worker)
        self._worker.error.connect(self._cleanup_worker)

        # Start processing
        self._worker_thread.start()

    def _on_processing_complete(self, answer: MCQAnswer):
        """Handle completed AI processing."""
        self.processing = False

        if answer.success:
            self.ui_manager.show_answer(
                answer.answer,
                answer.explanation,
                Config.POPUP_DURATION_MS
            )
        else:
            self.ui_manager.show_error(answer.error_message)

    def _on_processing_error(self, error_message: str):
        """Handle processing error."""
        self.processing = False
        self.ui_manager.show_error(error_message)

    def _cleanup_worker(self):
        """Clean up worker thread."""
        if self._worker_thread:
            self._worker_thread.quit()
            self._worker_thread.wait()
            self._worker_thread = None
            self._worker = None


# ============================================================================
# Entry Point
# ============================================================================

def main():
    """Main entry point."""
    print("Checking Ollama connection...")

    # Check if Ollama is running
    try:
        response = requests.get(f"{Config.OLLAMA_URL}/api/tags", timeout=3)
        if response.status_code != 200:
            print("ERROR: Cannot connect to Ollama!")
            print()
            print("To fix this:")
            print("1. Download Ollama from: https://ollama.ai")
            print("2. Install and run it")
            print("3. In a terminal, run: ollama pull mistral")
            print("4. Then start the app again")
            print()
            input("Press Enter to exit...")
            sys.exit(1)
    except Exception:
        print("ERROR: Cannot connect to Ollama!")
        print()
        print("To fix this:")
        print("1. Download Ollama from: https://ollama.ai")
        print("2. Install and run it")
        print("3. In a terminal, run: ollama pull mistral")
        print("4. Then start the app again")
        print()
        input("Press Enter to exit...")
        sys.exit(1)

    # Check for Tesseract
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
    except Exception:
        print("WARNING: Tesseract OCR may not be installed or configured.")
        print("Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print()

    # Create and start the assistant
    assistant = MCQAssistant()

    try:
        assistant.start()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
