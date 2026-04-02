"""
Screen Capture Module
=====================
Handles screen region selection with crosshair cursor and screenshot capture.
Uses mss for fast, efficient screen capture.
"""

import mss
import mss.tools
from PIL import Image
from typing import Optional, Tuple
import io


class ScreenCapture:
    """
    Handles screen capture operations.
    Optimized for speed with mss library.
    """

    def __init__(self):
        """Initialize the screen capture with mss instance."""
        self._sct = mss.mss()

    def capture_region(self, x1: int, y1: int, x2: int, y2: int) -> Optional[Image.Image]:
        """
        Capture a specific region of the screen.

        Args:
            x1: Left coordinate
            y1: Top coordinate
            x2: Right coordinate
            y2: Bottom coordinate

        Returns:
            PIL Image of the captured region, or None if failed
        """
        try:
            # Ensure coordinates are in correct order
            left = min(x1, x2)
            top = min(y1, y2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)

            # Minimum size check
            if width < 10 or height < 10:
                return None

            # Define the region to capture
            monitor = {
                "left": left,
                "top": top,
                "width": width,
                "height": height
            }

            # Capture the screen region
            screenshot = self._sct.grab(monitor)

            # Convert to PIL Image (RGB format for OCR)
            img = Image.frombytes(
                "RGB",
                (screenshot.width, screenshot.height),
                screenshot.rgb
            )

            return img

        except Exception as e:
            print(f"Screen capture error: {e}")
            return None

    def capture_full_screen(self, monitor_index: int = 1) -> Optional[Image.Image]:
        """
        Capture the entire screen.

        Args:
            monitor_index: Monitor to capture (1 = primary)

        Returns:
            PIL Image of the full screen
        """
        try:
            monitor = self._sct.monitors[monitor_index]
            screenshot = self._sct.grab(monitor)

            img = Image.frombytes(
                "RGB",
                (screenshot.width, screenshot.height),
                screenshot.rgb
            )

            return img

        except Exception as e:
            print(f"Full screen capture error: {e}")
            return None

    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get the primary screen dimensions.

        Returns:
            Tuple of (width, height)
        """
        monitor = self._sct.monitors[1]  # Primary monitor
        return monitor["width"], monitor["height"]

    def __del__(self):
        """Cleanup mss instance."""
        try:
            self._sct.close()
        except:
            pass


# Singleton instance for performance
_capture_instance: Optional[ScreenCapture] = None


def get_screen_capture() -> ScreenCapture:
    """
    Get or create the singleton ScreenCapture instance.

    Returns:
        ScreenCapture instance
    """
    global _capture_instance
    if _capture_instance is None:
        _capture_instance = ScreenCapture()
    return _capture_instance
