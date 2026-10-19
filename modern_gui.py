
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Excel Merger Pro | Modern")
        self.resize(1100, 700)
        self.setMinimumSize(850, 550)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #10111B;
            }

            QLabel {
                color: #F4F4FA;
                font-family: "Segoe UI";
            }

            QFrame#sidebar {
                background-color: #1B1D2B;
                border-radius: 16px;
            }

            QPushButton {
                background-color: #292C40;
                color: #F4F4FA;
                border: none;
                border-radius: 10px;
                padding: 14px;
                text-align: left;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #383B57;
            }

            QPushButton#primary {
                background-color: #8B5CF6;
                font-weight: bold;
            }

            QPushButton#primary:hover {
                background-color: #7547DF;
            }
        """)

        container = QWidget()
        self.setCentralWidget(container)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 25, 18, 25)
        sidebar_layout.setSpacing(12)

        logo = QLabel("◆  EXCEL MERGER")
        logo.setStyleSheet(
            "font-size: 17px; font-weight: bold;"
        )

        merge_button = QPushButton("Merge Files")
        join_button = QPushButton("Join Tables")

        sidebar_layout.addWidget(logo)
        sidebar_layout.addSpacing(35)
        sidebar_layout.addWidget(merge_button)
        sidebar_layout.addWidget(join_button)
        sidebar_layout.addStretch()

        version = QLabel("Modern UI Preview")
        version.setStyleSheet("color: #9295AD;")
        sidebar_layout.addWidget(version)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(18)

        title = QLabel("Welcome to Excel Merger Pro")
        title.setStyleSheet(
            "font-size: 29px; font-weight: bold;"
        )

        subtitle = QLabel(
            "Merge, organize and transform your files."
        )
        subtitle.setStyleSheet(
            "color: #A5A8BD; font-size: 15px;"
        )

        start_button = QPushButton("Start Merging")
        start_button.setObjectName("primary")
        start_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        start_button.setFixedWidth(200)

        content_layout.addStretch()
        content_layout.addWidget(title)
        content_layout.addWidget(subtitle)
        content_layout.addSpacing(20)
        content_layout.addWidget(start_button)
        content_layout.addStretch()

        layout.addWidget(sidebar)
        layout.addWidget(content, 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
