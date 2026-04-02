"""
UI Overlay Module
=================
Handles all UI elements including:
- Screen selection overlay with crosshair cursor
- Answer popup with fade animations
- Modern, minimal design using PyQt5
"""

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QGraphicsOpacityEffect, QDesktopWidget
)
from PyQt5.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve,
    QPoint, QRect, pyqtSignal, QObject
)
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QFont, QCursor,
    QPixmap, QBrush, QLinearGradient
)
from typing import Optional, Tuple, Callable
import sys


class SelectionOverlay(QWidget):
    """
    Full-screen transparent overlay for region selection.
    Shows crosshair cursor and selection rectangle.
    """

    # Signal emitted when selection is complete
    selection_made = pyqtSignal(int, int, int, int)
    selection_cancelled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.start_pos: Optional[QPoint] = None
        self.current_pos: Optional[QPoint] = None
        self.is_selecting = False

        self._setup_ui()

    def _setup_ui(self):
        """Configure the overlay window."""
        # Frameless, always on top, transparent
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Cover all screens
        desktop = QDesktopWidget()
        geometry = desktop.screenGeometry()

        # Get full virtual desktop bounds (all monitors)
        full_rect = QRect()
        for i in range(desktop.screenCount()):
            full_rect = full_rect.united(desktop.screenGeometry(i))

        self.setGeometry(full_rect)

        # Crosshair cursor
        self.setCursor(Qt.CrossCursor)

    def showEvent(self, event):
        """Handle show event."""
        super().showEvent(event)
        self.activateWindow()
        self.raise_()

    def paintEvent(self, event):
        """Draw the overlay and selection rectangle."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Semi-transparent dark overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

        # Draw selection rectangle if selecting
        if self.start_pos and self.current_pos:
            rect = QRect(self.start_pos, self.current_pos).normalized()

            # Clear the selection area (make it visible)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(rect, Qt.transparent)

            # Draw selection border
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            pen = QPen(QColor(74, 144, 226), 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRect(rect)

            # Draw corner handles
            handle_size = 8
            handle_color = QColor(74, 144, 226)
            painter.setBrush(handle_color)
            painter.setPen(Qt.NoPen)

            corners = [
                rect.topLeft(),
                rect.topRight(),
                rect.bottomLeft(),
                rect.bottomRight()
            ]
            for corner in corners:
                painter.drawEllipse(corner, handle_size // 2, handle_size // 2)

            # Draw dimensions
            width = rect.width()
            height = rect.height()
            dim_text = f"{width} × {height}"

            painter.setPen(QColor(255, 255, 255))
            font = QFont("Segoe UI", 10)
            painter.setFont(font)

            # Position dimensions below selection
            text_pos = QPoint(
                rect.center().x() - 30,
                rect.bottom() + 20
            )
            painter.drawText(text_pos, dim_text)

    def mousePressEvent(self, event):
        """Handle mouse press to start selection."""
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.current_pos = event.pos()
            self.is_selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        """Handle mouse move during selection."""
        if self.is_selecting:
            self.current_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release to complete selection."""
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            if self.start_pos and self.current_pos:
                # Emit the selection coordinates
                rect = QRect(self.start_pos, self.current_pos).normalized()
                if rect.width() > 10 and rect.height() > 10:
                    # Account for window position offset
                    global_start = self.mapToGlobal(rect.topLeft())
                    self.selection_made.emit(
                        global_start.x(),
                        global_start.y(),
                        global_start.x() + rect.width(),
                        global_start.y() + rect.height()
                    )
                else:
                    self.selection_cancelled.emit()
            self.close()

    def keyPressEvent(self, event):
        """Handle escape key to cancel."""
        if event.key() == Qt.Key_Escape:
            self.selection_cancelled.emit()
            self.close()


class AnswerPopup(QWidget):
    """
    Modern, semi-transparent popup to display MCQ answers.
    Features fade-in/fade-out animations.
    """

    def __init__(self, answer: str, explanation: str, is_error: bool = False):
        super().__init__()
        self.answer = answer
        self.explanation = explanation
        self.is_error = is_error

        self._setup_ui()
        self._setup_animations()

    def _setup_ui(self):
        """Configure the popup window and layout."""
        # Window flags for overlay popup
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Fixed size
        self.setFixedSize(320, 100)

        # Position at bottom-right of primary screen
        desktop = QDesktopWidget()
        screen_rect = desktop.availableGeometry(desktop.primaryScreen())
        self.move(
            screen_rect.right() - self.width() - 20,
            screen_rect.bottom() - self.height() - 20
        )

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)

        # Answer label
        self.answer_label = QLabel()
        if self.is_error:
            self.answer_label.setText("Error")
            self.answer_label.setStyleSheet("""
                QLabel {
                    color: #ff6b6b;
                    font-size: 24px;
                    font-weight: bold;
                    font-family: 'Segoe UI', Arial;
                }
            """)
        else:
            self.answer_label.setText(f"Answer: {self.answer}")
            self.answer_label.setStyleSheet("""
                QLabel {
                    color: #4ade80;
                    font-size: 24px;
                    font-weight: bold;
                    font-family: 'Segoe UI', Arial;
                }
            """)
        layout.addWidget(self.answer_label)

        # Explanation label
        self.explanation_label = QLabel(self.explanation)
        self.explanation_label.setWordWrap(True)
        self.explanation_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.85);
                font-size: 12px;
                font-family: 'Segoe UI', Arial;
            }
        """)
        layout.addWidget(self.explanation_label)

        # Opacity effect for fade animations
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0)
        self.setGraphicsEffect(self.opacity_effect)

    def paintEvent(self, event):
        """Draw rounded rectangle background with gradient."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Rounded rectangle with gradient background
        rect = self.rect()
        radius = 12

        # Dark gradient background
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor(30, 30, 35, 240))
        gradient.setColorAt(1, QColor(20, 20, 25, 240))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, radius, radius)

        # Subtle border
        border_pen = QPen(QColor(60, 60, 70), 1)
        painter.setPen(border_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(rect.adjusted(0, 0, -1, -1), radius, radius)

    def _setup_animations(self):
        """Configure fade-in and fade-out animations."""
        # Fade in animation
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(200)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)

        # Fade out animation
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(300)
        self.fade_out.setStartValue(1)
        self.fade_out.setEndValue(0)
        self.fade_out.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out.finished.connect(self.close)

        # Timer for auto-dismiss
        self.dismiss_timer = QTimer(self)
        self.dismiss_timer.setSingleShot(True)
        self.dismiss_timer.timeout.connect(self._start_fade_out)

    def show_animated(self, duration_ms: int = 3000):
        """
        Show the popup with fade-in animation.

        Args:
            duration_ms: How long to show before fading out
        """
        self.show()
        self.fade_in.start()
        self.dismiss_timer.start(duration_ms)

    def _start_fade_out(self):
        """Start the fade-out animation."""
        self.fade_out.start()

    def mousePressEvent(self, event):
        """Dismiss on click."""
        self._start_fade_out()


class LoadingPopup(QWidget):
    """
    Small loading indicator popup.
    """

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._setup_animation()
        self._dots = 0

    def _setup_ui(self):
        """Configure the loading popup."""
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setFixedSize(150, 50)

        # Position at bottom-right
        desktop = QDesktopWidget()
        screen_rect = desktop.availableGeometry(desktop.primaryScreen())
        self.move(
            screen_rect.right() - self.width() - 20,
            screen_rect.bottom() - self.height() - 20
        )

        # Label
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        self.label = QLabel("Processing")
        self.label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                font-family: 'Segoe UI', Arial;
            }
        """)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

    def paintEvent(self, event):
        """Draw background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QColor(30, 30, 35, 230))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)

    def _setup_animation(self):
        """Setup dot animation timer."""
        self.dot_timer = QTimer(self)
        self.dot_timer.timeout.connect(self._update_dots)

    def _update_dots(self):
        """Animate loading dots."""
        self._dots = (self._dots + 1) % 4
        dots = "." * self._dots
        self.label.setText(f"Processing{dots}")

    def show(self):
        """Show with animation."""
        super().show()
        self.dot_timer.start(300)

    def close(self):
        """Stop animation and close."""
        self.dot_timer.stop()
        super().close()


class UIManager(QObject):
    """
    Manages all UI components and interactions.
    Provides a clean interface for the main application.
    """

    def __init__(self):
        super().__init__()
        self._app: Optional[QApplication] = None
        self._selection_overlay: Optional[SelectionOverlay] = None
        self._current_popup: Optional[AnswerPopup] = None
        self._loading_popup: Optional[LoadingPopup] = None

    def ensure_app(self):
        """Ensure QApplication exists."""
        if self._app is None:
            self._app = QApplication.instance()
            if self._app is None:
                self._app = QApplication(sys.argv)

    def start_selection(self, callback: Callable[[int, int, int, int], None],
                       cancel_callback: Optional[Callable[[], None]] = None):
        """
        Show the selection overlay.

        Args:
            callback: Function to call with selection coordinates
            cancel_callback: Function to call if selection is cancelled
        """
        self.ensure_app()

        # Close any existing overlay
        if self._selection_overlay:
            self._selection_overlay.close()

        self._selection_overlay = SelectionOverlay()

        def on_selection(x1, y1, x2, y2):
            callback(x1, y1, x2, y2)

        def on_cancel():
            if cancel_callback:
                cancel_callback()

        self._selection_overlay.selection_made.connect(on_selection)
        self._selection_overlay.selection_cancelled.connect(on_cancel)
        self._selection_overlay.showFullScreen()

    def show_loading(self):
        """Show loading indicator."""
        self.ensure_app()

        if self._loading_popup:
            self._loading_popup.close()

        self._loading_popup = LoadingPopup()
        self._loading_popup.show()

    def hide_loading(self):
        """Hide loading indicator."""
        if self._loading_popup:
            self._loading_popup.close()
            self._loading_popup = None

    def show_answer(self, answer: str, explanation: str, duration_ms: int = 3000):
        """
        Show the answer popup.

        Args:
            answer: The answer letter (A, B, C, D)
            explanation: Short explanation
            duration_ms: How long to show
        """
        self.ensure_app()
        self.hide_loading()

        # Close any existing popup
        if self._current_popup:
            self._current_popup.close()

        self._current_popup = AnswerPopup(answer, explanation, is_error=False)
        self._current_popup.show_animated(duration_ms)

    def show_error(self, message: str, duration_ms: int = 4000):
        """
        Show an error popup.

        Args:
            message: Error message to display
            duration_ms: How long to show
        """
        self.ensure_app()
        self.hide_loading()

        if self._current_popup:
            self._current_popup.close()

        self._current_popup = AnswerPopup("", message, is_error=True)
        self._current_popup.show_animated(duration_ms)

    def process_events(self):
        """Process Qt events (call from main loop)."""
        if self._app:
            self._app.processEvents()


# Singleton instance
_ui_manager: Optional[UIManager] = None


def get_ui_manager() -> UIManager:
    """Get or create the singleton UIManager instance."""
    global _ui_manager
    if _ui_manager is None:
        _ui_manager = UIManager()
    return _ui_manager
