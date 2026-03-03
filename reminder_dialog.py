# -*- coding: utf-8 -*-
"""Qt reminder dialog styled with QSS. Exit 0 = user clicked Open, 1 = closed without action."""
import sys
import os

try:
    from PyQt5.QtWidgets import (
        QApplication, QDialog, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QFrame, QWidget, QSizePolicy
    )
    from PyQt5.QtCore import Qt, QPoint
    from PyQt5.QtGui import QIcon, QPixmap
    from PyQt5.QtSvg import QSvgWidget
    HAS_SVG = True
except ImportError:
    from PyQt5.QtWidgets import (
        QApplication, QDialog, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QFrame, QWidget, QSizePolicy
    )
    from PyQt5.QtCore import Qt, QPoint
    from PyQt5.QtGui import QIcon, QPixmap
    HAS_SVG = False


class DraggableArea(QWidget):
    """Widget that allows moving the parent window by click-and-drag."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_start_global = None
        self._drag_start_window = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start_global = event.globalPos()
            self._drag_start_window = self.window().pos()
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_start_global is not None and (event.buttons() & Qt.LeftButton):
            delta = event.globalPos() - self._drag_start_global
            self.window().move(self._drag_start_window + delta)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start_global = None
            self._drag_start_window = None
            self.setCursor(Qt.OpenHandCursor)
        super().mouseReleaseEvent(event)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SVG_PATH = os.path.join(SCRIPT_DIR, "Alarm Clock.svg")

# QSS - iOS-style dark modal, Calibri font
QSS = """
QDialog {
    font-family: "Calibri", "Segoe UI", sans-serif;
    background-color: #1C1C1E;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.08);
}
QFrame#content {
    background-color: transparent;
    border: none;
    border-radius: 14px;
}
QLabel#title {
    font-family: "Calibri", "Segoe UI", sans-serif;
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 600;
    letter-spacing: -0.02em;
}
QLabel#subtitle {
    font-family: "Calibri", "Segoe UI", sans-serif;
    color: #8E8E93;
    font-size: 15px;
    line-height: 1.4;
}
QPushButton#actionBtn {
    font-family: "Calibri", "Segoe UI", sans-serif;
    background-color: #0A84FF;
    color: #FFFFFF;
    font-size: 17px;
    font-weight: 600;
    border: none;
    border-radius: 10px;
    padding: 14px 20px;
    min-height: 24px;
    min-width: 0;
}
QPushButton#actionBtn:hover {
    background-color: #409CFF;
}
QPushButton#actionBtn:pressed {
    background-color: #0066CC;
}
QPushButton#cancelBtn {
    font-family: "Calibri", "Segoe UI", sans-serif;
    background-color: transparent;
    color: #8E8E93;
    font-size: 17px;
    font-weight: 600;
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 10px;
    padding: 14px 20px;
    min-height: 24px;
    min-width: 0;
}
QPushButton#cancelBtn:hover {
    background-color: rgba(255,255,255,0.08);
    color: #FFFFFF;
}
QPushButton#cancelBtn:pressed {
    background-color: rgba(255,255,255,0.12);
}
"""


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)

    d = QDialog(None, Qt.Dialog | Qt.FramelessWindowHint)
    d.setAttribute(Qt.WA_TranslucentBackground, False)
    d.setWindowTitle("Release Track Reminder")
    d.setFixedSize(380, 320)
    layout = QVBoxLayout(d)
    layout.setSpacing(16)
    layout.setContentsMargins(32, 28, 32, 28)

    draggable = DraggableArea(d)
    draggable.setCursor(Qt.OpenHandCursor)
    draggable_layout = QVBoxLayout(draggable)
    draggable_layout.setContentsMargins(0, 0, 0, 0)
    draggable_layout.setSpacing(0)

    content = QFrame(draggable)
    content.setObjectName("content")
    vbox = QVBoxLayout(content)
    vbox.setSpacing(12)
    vbox.setContentsMargins(0, 0, 0, 0)

    # Icon: Alarm Clock.svg
    icon_container = QWidget()
    icon_layout = QHBoxLayout(icon_container)
    icon_layout.setContentsMargins(0, 0, 0, 8)
    icon_layout.setAlignment(Qt.AlignCenter)
    if HAS_SVG and os.path.exists(SVG_PATH):
        from PyQt5.QtWidgets import QGraphicsColorizeEffect
        from PyQt5.QtGui import QColor
        svg = QSvgWidget(SVG_PATH)
        svg.setFixedSize(64, 64)
        effect = QGraphicsColorizeEffect()
        effect.setColor(QColor("#0A84FF"))
        effect.setStrength(1.0)
        svg.setGraphicsEffect(effect)
        icon_layout.addWidget(svg)
    else:
        lbl_icon = QLabel("\u23F0")  # alarm emoji fallback
        lbl_icon.setStyleSheet("font-size: 48px; color: #0A84FF;")
        lbl_icon.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(lbl_icon)

    vbox.addWidget(icon_container)

    title = QLabel("Weekly Release Track")
    title.setObjectName("title")
    title.setAlignment(Qt.AlignCenter)
    title.setWordWrap(True)
    vbox.addWidget(title)

    subtitle = QLabel("Open folder & Box link to continue.")
    subtitle.setObjectName("subtitle")
    subtitle.setAlignment(Qt.AlignCenter)
    subtitle.setWordWrap(True)
    vbox.addWidget(subtitle)

    draggable_layout.addWidget(content)
    layout.addWidget(draggable)

    btn_layout = QHBoxLayout()
    btn_layout.setSpacing(12)
    btn_layout.addStretch()
    btn_cancel = QPushButton("Cancel")
    btn_cancel.setObjectName("cancelBtn")
    btn_cancel.setCursor(Qt.PointingHandCursor)
    btn_cancel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    btn = QPushButton("Open Folder & Box")
    btn.setObjectName("actionBtn")
    btn.setCursor(Qt.PointingHandCursor)
    btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    btn_layout.addWidget(btn_cancel)
    btn_layout.addWidget(btn)
    btn_layout.addStretch()
    layout.addLayout(btn_layout)

    result = [1]

    def on_open():
        result[0] = 0
        d.accept()

    def on_cancel():
        result[0] = 1
        d.reject()

    btn.clicked.connect(on_open)
    btn_cancel.clicked.connect(on_cancel)
    d.finished.connect(lambda: sys.exit(result[0]))

    # Center on screen
    from PyQt5.QtWidgets import QDesktopWidget
    geo = d.frameGeometry()
    geo.moveCenter(QDesktopWidget().availableGeometry().center())
    d.move(geo.topLeft())

    d.exec_()
    sys.exit(result[0])


if __name__ == "__main__":
    main()
