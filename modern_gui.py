import sys
from pathlib import Path
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QListWidget,
    QMessageBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from universal_merge import merge_files



class MergeWorker(QThread):
    progress = Signal(str)
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, input_folder, output_folder):
        super().__init__()
        self.input_folder = input_folder
        self.output_folder = output_folder

    def run(self):
        try:
            result = merge_files(
                self.input_folder,
                self.output_folder,
                progress=self.progress.emit
            )
            self.completed.emit(result)

        except Exception as error:
            self.failed.emit(str(error))



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

        merge_button.clicked.connect(self.select_files)

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
        self.start_button = start_button
        start_button.clicked.connect(self.start_merge)
        start_button.setObjectName("primary")
        start_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        start_button.setFixedWidth(200)

        content_layout.addStretch()
        content_layout.addWidget(title)
        content_layout.addWidget(subtitle)
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(160)

        content_layout.addWidget(self.file_list)
        self.output_folder = ""

        self.output_button = QPushButton("Choose Output Folder")
        self.output_button.clicked.connect(self.choose_output_folder)

        self.output_label = QLabel("No output folder selected")
        self.output_label.setStyleSheet(
        "color: #A5A8BD; font-size: 13px;"
        )

        content_layout.addWidget(self.output_button)
        content_layout.addWidget(self.output_label)
        content_layout.addSpacing(20)
        content_layout.addWidget(start_button)
        content_layout.addStretch()

        layout.addWidget(sidebar)
        layout.addWidget(content, 1)


    
    def select_files(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose Folder Containing Excel or CSV Files"
        )

        if not folder:
            return

        folder_path = Path(folder)
        self.input_folder = str(folder_path)
        supported_extensions = {".xlsx", ".xls", ".csv"}

        files = sorted(
            str(file)
            for file in folder_path.iterdir()
            if file.is_file()
            and file.suffix.lower() in supported_extensions
            and not file.name.startswith("~$")
        )

        self.selected_files = files
        self.file_list.clear()

        for file in files:
            self.file_list.addItem(Path(file).name)

        if not files:
            self.file_list.addItem(
                "No Excel or CSV files found in this folder."
            )


    def choose_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose Output Folder"
        )

        if folder:
            self.output_folder = folder
            self.output_label.setText(
                f"Save to: {folder}"
            )      


    
    def start_merge(self):
        if getattr(self, "worker", None) is not None:
            if self.worker.isRunning():
                return

        if not getattr(self, "input_folder", ""):
            QMessageBox.warning(
                self, "Missing Input",
                "Please select an input folder."
            )
            return

        if not getattr(self, "selected_files", []):
            QMessageBox.warning(
                self, "No Files",
                "No supported files were found."
            )
            return

        if not getattr(self, "output_folder", ""):
            QMessageBox.warning(
                self, "Missing Output",
                "Please select an output folder."
            )
            return

        self.start_button.setEnabled(False)
        self.start_button.setText("Processing...")

        self.worker = MergeWorker(
            self.input_folder,
            self.output_folder
        )

        self.worker.progress.connect(self.show_progress)
        self.worker.completed.connect(self.merge_completed)
        self.worker.failed.connect(self.merge_failed)
        self.worker.start()

    def show_progress(self, message):
        self.start_button.setText(str(message))

    def merge_completed(self, result):
        self.start_button.setEnabled(True)
        self.start_button.setText("Start Merging")

        QMessageBox.information(
            self,
            "Merge Completed",
            f"Result: {result}"
        )

    def merge_failed(self, error):
        self.start_button.setEnabled(True)
        self.start_button.setText("Start Merging")

        QMessageBox.critical(
            self,
            "Merge Failed",
            str(error)
        )


    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
