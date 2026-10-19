import sys
from pathlib import Path
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QDialog,
    QListWidget,
    QMessageBox,
    QProgressBar,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from universal_merge import merge_files
from universal_merge import list_input_files, read_file
from type_suggestions import suggest_column_types
from column_types_dialog import ColumnTypesDialog
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl


class MergeWorker(QThread):
    progress = Signal(str)
    completed = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        input_folder,
        output_folder,
        column_types=None
    ):
        super().__init__()

        self.input_folder = input_folder
        self.output_folder = output_folder
        self.column_types = column_types or {}

    def run(self):
        try:
            result = merge_files(
            self.input_folder,
            self.output_folder,
            progress=self.progress.emit,
            column_types=self.column_types
            )
            self.completed.emit(result)

        except Exception as error:
            self.failed.emit(str(error))



            
class InspectionWorker(QThread):
    completed = Signal(dict)
    failed = Signal(str)

    def __init__(self, input_folder):
        super().__init__()
        self.input_folder = input_folder

    def run(self):
        try:
            paths = list_input_files(
                Path(self.input_folder)
            )

            if not paths:
                raise ValueError(
                    "No CSV or XLSX files found."
                )

            column_votes = {}

            for path in paths:
                df = read_file(path)

                suggestions = suggest_column_types(df)

                for column, suggestion in suggestions.items():
                    column_votes.setdefault(
                        column, []
                    ).append(suggestion)

            final_suggestions = {}

            for column, votes in column_votes.items():
                if all(
                    vote == "Number"
                    for vote in votes
                ):
                    final_suggestions[column] = "Number"
                else:
                    final_suggestions[column] = "Keep Original"

            self.completed.emit(final_suggestions)

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
        self.merge_button = merge_button

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
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)

        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #292C40;
                border: none;
                border-radius: 4px;
            }

            QProgressBar::chunk {
                background-color: #8B5CF6;
                border-radius: 4px;
            }
        """)

        self.progress_bar.hide()

        self.status_label = QLabel("Ready to merge")
        self.status_label.setStyleSheet(
            "color: #A5A8BD; font-size: 13px;"
        )

        content_layout.addWidget(self.progress_bar)
        content_layout.addWidget(self.status_label)
        self.open_report_button = QPushButton("Open Report")
        self.open_report_button.setFixedWidth(200)
        self.open_report_button.setEnabled(False)
        self.open_report_button.clicked.connect(self.open_report)

        content_layout.addWidget(self.open_report_button)

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

        supported_extensions = {".xlsx", ".csv"}

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
        if getattr(self, "_busy", False):
            return

        source = getattr(self, "input_folder", "")
        output = getattr(self, "output_folder", "")

        if not source or not Path(source).is_dir():
            QMessageBox.warning(
                self, "Missing Input",
                "Please select a valid input folder."
            )
            return

        if not getattr(self, "selected_files", []):
            QMessageBox.warning(
                self, "No Files",
                "No supported files were found."
            )
            return

        if not output or not Path(output).is_dir():
            QMessageBox.warning(
                self, "Missing Output",
                "Please select a valid output folder."
            )
            return

        if Path(source).resolve() == Path(output).resolve():
            QMessageBox.warning(
                self, "Invalid Folders",
                "Input and output folders must be different."
            )
            return

        self._busy = True
        self.start_button.setEnabled(False)
        self.merge_button.setEnabled(False)
        self.output_button.setEnabled(False)
        self.start_button.setText("Inspecting columns...")
        self.status_label.setText("Inspecting columns...")
        self.progress_bar.show()

        self.inspection_result = None
        self.inspection_error = None

        self.inspection_worker = InspectionWorker(source)

        self.inspection_worker.completed.connect(
            self.store_inspection
        )
        self.inspection_worker.failed.connect(
            self.store_inspection_error
        )
        self.inspection_worker.finished.connect(
            self.finish_inspection
        )

        self.inspection_worker.start()


    def show_progress(self, message):
        self.status_label.setText(str(message))

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


    def store_inspection(self, suggestions):
        self.inspection_result = suggestions

    def store_inspection_error(self, error):
        self.inspection_error = error

    def unlock_processing(self):
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        self._busy = False
        self.start_button.setEnabled(True)
        self.merge_button.setEnabled(True)
        self.output_button.setEnabled(True)
        self.start_button.setText("Start Merging")

    def finish_inspection(self):
        if self.inspection_error:
            self.unlock_processing()
            QMessageBox.critical(
                self, "Inspection Failed",
                self.inspection_error
            )
            return

        if self.inspection_result is None:
            self.unlock_processing()
            QMessageBox.critical(
                self, "Inspection Failed",
                "No inspection result was returned."
            )
            return

            self.progress_bar.hide()
            self.status_label.setText("Waiting for column type approval...")

        dialog = ColumnTypesDialog(
            self.inspection_result
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            self.unlock_processing()
            return

        type_mapping = {
            "Number": "number",
            "Text": "text"
        }

        approved_types = {
            column: type_mapping[choice]
            for column, choice in dialog.choices.items()
            if choice in type_mapping
        }

        self.merge_result = None
        self.merge_error = None

        self.start_button.setText("Merging...")
        self.status_label.setText("Merging files...")
        self.progress_bar.show()

        self.worker = MergeWorker(
            self.input_folder,
            self.output_folder,
            column_types=approved_types
        )

        self.worker.progress.connect(self.show_progress)
        self.worker.completed.connect(self.store_merge_result)
        self.worker.failed.connect(self.store_merge_error)
        self.worker.finished.connect(self.finish_merge)

        self.worker.start()

    def store_merge_result(self, result):
        self.merge_result = result

    def store_merge_error(self, error):
        self.merge_error = error

    def finish_merge(self):
        self.unlock_processing()

        if self.merge_error:
            QMessageBox.critical(
                self, "Merge Failed",
                self.merge_error
            )
            return

        if self.merge_result is None:
            QMessageBox.critical(
                self, "Merge Failed",
                "No merge result was returned."
            )
            return

        result = self.merge_result
        self.report_path = result["report"]
        self.open_report_button.setEnabled(True)

        
        QMessageBox.information(
            self,
            "Merge Completed",
            f"Files: {result['files']}\n"
            f"Rows: {result['clean_rows']}\n"
            f"Report: {result['report']}"
        )



    def open_report(self):
        report = getattr(self, "report_path", "")

        if not report or not Path(report).is_file():
            QMessageBox.warning(
                self,
                "Report Not Found",
                "The report file could not be found."
            )
            return

        opened = QDesktopServices.openUrl(
            QUrl.fromLocalFile(str(Path(report).resolve()))
        )

        if not opened:
         QMessageBox.warning(
            self,
            "Open Failed",
            "Could not open the Excel report."
        )


    def closeEvent(self, event):
        if getattr(self, "_busy", False):
            QMessageBox.warning(
                self,
                "Processing",
                "Please wait until processing finishes."
            )
            event.ignore()
            return

        super().closeEvent(event)

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
