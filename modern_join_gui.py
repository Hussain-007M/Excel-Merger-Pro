
import sys
from pathlib import Path

import pandas as pd

from PySide6.QtCore import Qt, QThread, Signal, QUrl, QTimer
from PySide6.QtGui import QDesktopServices

from join_engine import join_tables
from PySide6.QtWidgets import (
    QApplication,
    QScrollArea,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

class NoWheelComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()

class JoinWorker(QThread):
    completed = Signal(str)
    failed = Signal(str)

    def __init__(
        self,
        left_file,
        right_file,
        output_folder,
        join_type,
        left_key,
        right_key
    ):
        super().__init__()

        self.left_file = left_file
        self.right_file = right_file
        self.output_folder = output_folder
        self.join_type = join_type
        self.left_key = left_key
        self.right_key = right_key

    def run(self):
        try:
            join_tables(
             left_file=self.left_file,
             right_file=self.right_file,
             output_folder=self.output_folder,
             join_type=self.join_type,
             left_key=self.left_key,
             right_key=self.right_key,
             readable_ids=False
)

            report_path = str(
                Path(self.output_folder) / "Joined_Data.xlsx"
            )

            self.completed.emit(report_path)

        except Exception as error:
            self.failed.emit(str(error))





class JoinWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tabrion | Join Tables")
        self.resize(950, 650)
        self.setMinimumSize(750, 550)

        self.left_file = None
        self.right_file = None

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #10111B;
                color: #F4F4FA;
                font-family: "Segoe UI";
            }

            QLabel {
            font-size: 13px;
            background: transparent;
            }

            QFrame#tableCard {
                background-color: #1B1D2B;
                border-radius: 12px;
            }

            QPushButton {
                background-color: #292C40;
                border: none;
                border-radius: 9px;
                padding: 13px;
                text-align: left;
                font-size: 13px;
            }

            QPushButton:hover {
                background-color: #363A56;
            }

            QPushButton#joinButton {
                background-color: #8B5CF6;
                color: white;
                font-weight: bold;
                text-align: center;
            }

            QPushButton#joinButton:disabled {
                background-color: #39324F;
                color: #9994AD;
            }

            QComboBox {
                background-color: #292C40;
                border: none;
                border-radius: 7px;
                padding: 11px;
                min-height: 20px;
            }

            QComboBox QAbstractItemView {
                background-color: #292C40;
                color: white;
                selection-background-color: #8B5CF6;
            }
        """)

        scroll = QScrollArea()
        self.scroll_area = scroll
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
        Qt.ScrollBarPolicy.ScrollBarAlwaysOff
)

        
        root = QWidget()
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(scroll, 1)


        central = QWidget()
        scroll.setWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(32, 30, 32, 30)
        layout.setSpacing(18)

        title = QLabel("Join Tables")
        title.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        subtitle = QLabel(
            "Combine two tables using matching columns."
        )
        subtitle.setStyleSheet("color: #A5A8BD;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(16)

        # LEFT TABLE
        left_card = QFrame()
        left_card.setMinimumHeight(260)
        left_card.setObjectName("tableCard")

        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(20, 22, 20, 22)
        left_layout.setSpacing(14)

        left_title = QLabel("Left Table")
        left_title.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        self.left_button = QPushButton("Choose Left File")
        self.left_button.clicked.connect(
            lambda: self.select_file("left")
        )

        self.left_label = QLabel("No file selected")
        self.left_label.setWordWrap(True)
        self.left_label.setStyleSheet("color: #A5A8BD;")

        self.left_key = NoWheelComboBox()
        self.left_key.setEnabled(False)

        left_layout.addWidget(left_title)
        left_layout.addWidget(self.left_button)
        left_layout.addWidget(self.left_label)
        left_layout.addWidget(QLabel("Join Column"))
        left_layout.addWidget(self.left_key)
        left_layout.addStretch()

        # RIGHT TABLE
        right_card = QFrame()
        right_card.setMinimumHeight(260)
        right_card.setObjectName("tableCard")

        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(20, 22, 20, 22)
        right_layout.setSpacing(14)

        right_title = QLabel("Right Table")
        right_title.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        self.right_button = QPushButton("Choose Right File")
        self.right_button.clicked.connect(
            lambda: self.select_file("right")
        )

        self.right_label = QLabel("No file selected")
        self.right_label.setWordWrap(True)
        self.right_label.setStyleSheet("color: #A5A8BD;")

        self.right_key = NoWheelComboBox()
        self.right_key.setEnabled(False)

        right_layout.addWidget(right_title)
        right_layout.addWidget(self.right_button)
        right_layout.addWidget(self.right_label)
        right_layout.addWidget(QLabel("Join Column"))
        right_layout.addWidget(self.right_key)
        right_layout.addStretch()

        tables_layout.addWidget(left_card, 1)
        tables_layout.addWidget(right_card, 1)

        layout.addLayout(tables_layout)

        layout.addWidget(QLabel("Join Type"))

        self.join_type = NoWheelComboBox()
        self.join_type.addItems([
            "Left Join",
            "Inner Join"
        ])
        layout.addWidget(self.join_type)

        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        self.join_button = QPushButton("Start Joining")
        self.join_button.setObjectName("joinButton")
        self.join_button.setEnabled(False)
        self.join_button.clicked.connect(self.start_join)

        self.open_report_button = QPushButton("Open Report")
        self.open_report_button.setEnabled(False)
        self.open_report_button.clicked.connect(self.open_report)

        buttons_layout.addWidget(self.join_button, 1)
        buttons_layout.addWidget(self.open_report_button, 1)

        layout.addLayout(buttons_layout)

        self.report_path = None
        self.join_worker = None


        self.status_label = QLabel(
            "Select both files and their join columns."
        )
        self.status_label.setStyleSheet("color: #A5A8BD;")
        layout.addWidget(self.status_label)
        
        # JOIN results panel
        self.results_panel = QFrame()
        self.results_panel.setObjectName("joinResultsPanel")
        self.results_panel.setStyleSheet("""
            QFrame#joinResultsPanel {
                background-color: #1B1D2B;
                border-radius: 12px;
            }
        """)

        results_layout = QVBoxLayout(self.results_panel)
        results_layout.setContentsMargins(16, 14, 16, 14)
        results_layout.setSpacing(12)

        results_title = QLabel("Join Completed")
        results_title.setStyleSheet("""
            color: #4ADE80;
            background: transparent;
            font-size: 17px;
            font-weight: bold;
        """)
        results_layout.addWidget(results_title)

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)

        self.join_stat_labels = {}

        for key, label in [
            ("matched", "Matched"),
            ("unmatched", "Unmatched"),
            ("joined", "Joined Rows"),
        ]:
            card = QFrame()
            card.setObjectName("joinStatCard")
            card.setMinimumHeight(95)
            card.setStyleSheet("""
                QFrame#joinStatCard {
                    background-color: #292C40;
                    border-radius: 10px;
                }
                QFrame#joinStatCard QLabel {
                    background: transparent;
                }
            """)

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 10, 10, 10)
            card_layout.setSpacing(4)

            value_label = QLabel("0")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_label.setStyleSheet(
                "font-size: 24px; font-weight: bold;"
            )

            name_label = QLabel(label)
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setStyleSheet(
                "font-size: 12px; color: #A5A8BD;"
            )

            card_layout.addWidget(value_label)
            card_layout.addWidget(name_label)

            self.join_stat_labels[key] = value_label
            stats_layout.addWidget(card, 1)

        results_layout.addLayout(stats_layout)

        self.results_panel.hide()
        root_layout.addWidget(self.results_panel)
        
        self.left_key.activated.connect(
            self.invalidate_join_results
        )

        self.right_key.activated.connect(
            self.invalidate_join_results
        )

        self.join_type.activated.connect(
            self.invalidate_join_results
        )



    def read_columns(self, path):
        path = Path(path)

        if path.suffix.lower() == ".csv":
            try:
                df = pd.read_csv(
                    path,
                    nrows=0,
                    encoding="utf-8-sig"
                )
            except UnicodeDecodeError:
                df = pd.read_csv(
                    path,
                    nrows=0,
                    encoding="cp1252"
                )

        elif path.suffix.lower() == ".xlsx":
            df = pd.read_excel(path, nrows=0)

        else:
            raise ValueError("Unsupported file type")

        columns = [
            str(column).strip()
            for column in df.columns
        ]

        if len(columns) != len(set(columns)):
            raise ValueError("Duplicate column names found")

        return columns

    def select_file(self, side):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Excel or CSV File",
            "",
            "Data Files (*.xlsx *.csv)"
        )

        if not path:
            return

        try:
            columns = self.read_columns(path)

            if not columns:
                raise ValueError("No columns found")

        except Exception as error:
            QMessageBox.critical(
                self,
                "File Error",
                str(error)
            )
            return
        self.invalidate_join_results()
        if side == "left":
            self.left_file = path
            self.left_label.setText(Path(path).name)
            self.left_key.clear()
            self.left_key.addItems(columns)
            self.left_key.setEnabled(True)

        else:
            self.right_file = path
            self.right_label.setText(Path(path).name)
            self.right_key.clear()
            self.right_key.addItems(columns)
            self.right_key.setEnabled(True)

        if self.left_file and self.right_file:
            self.join_button.setEnabled(True)
            self.status_label.setText(
                "Both tables loaded. Ready to join."
            )




    def start_join(self):
        if not self.left_file or not self.right_file:
            return

        output_folder = QFileDialog.getExistingDirectory(
            self,
            "Choose Output Folder"
        )

        if not output_folder:
            return

        join_type = (
            "left"
            if self.join_type.currentIndex() == 0
            else "inner"
        )

        self.join_button.setEnabled(False)
        self.left_button.setEnabled(False)
        self.right_button.setEnabled(False)
        self.left_key.setEnabled(False)
        self.right_key.setEnabled(False)
        self.join_type.setEnabled(False)
        self.open_report_button.setEnabled(False)

        self.status_label.setText("Joining tables...")
        self.results_panel.hide()

        self.join_worker = JoinWorker(
            left_file=self.left_file,
            right_file=self.right_file,
            output_folder=output_folder,
            join_type=join_type,
            left_key=self.left_key.currentText(),
            right_key=self.right_key.currentText()
        )

        self.join_worker.completed.connect(
            self.join_completed
        )
        self.join_worker.failed.connect(
            self.join_failed
        )
        self.join_worker.finished.connect(
            self.restore_controls
        )

        self.join_worker.start()

    


    def invalidate_join_results(self):
        self.results_panel.hide()
        self.report_path = None
        self.open_report_button.setEnabled(False)

        if self.left_file and self.right_file:
            self.status_label.setText(
                "Settings changed. Ready to join."
            )
        else:
            self.status_label.setText(
                "Select both files and their join columns."
            )




    
    def join_completed(self, report_path, stats=None):
        self.report_path = report_path
        self.open_report_button.setEnabled(True)

        try:
            # Use worker statistics if available
            if stats is None:
                summary = pd.read_excel(
                    report_path,
                    sheet_name="Join Summary"
                )

                stats = dict(
                    zip(summary["Metric"], summary["Value"])
                )

            self.join_stat_labels["matched"].setText(
                str(int(stats["Matched Rows"]))
            )

            self.join_stat_labels["unmatched"].setText(
                str(int(stats["Unmatched Left Rows"]))
            )

            self.join_stat_labels["joined"].setText(
                str(int(stats["Joined Rows"]))
            )

            self.results_panel.show()

            self.status_label.setText(
                "Join completed. Your report is ready."
            )

        except Exception as error:
            self.results_panel.hide()
            self.status_label.setText(
                "Join completed, but statistics could not be displayed."
            )
            print("JOIN statistics error:", error)



    def join_failed(self, message):
        self.status_label.setText("Join failed.")

        QMessageBox.critical(
            self,
            "Join Error",
            message
        )

    
    def restore_controls(self):
        self.join_button.setEnabled(True)
        self.left_button.setEnabled(True)
        self.right_button.setEnabled(True)
        self.left_key.setEnabled(True)
        self.right_key.setEnabled(True)
        self.join_type.setEnabled(True)


        # Keep completed results visible in the scroll areas


    def open_report(self):
        if self.report_path and Path(self.report_path).is_file():
            QDesktopServices.openUrl(
                QUrl.fromLocalFile(self.report_path)
            )

    def closeEvent(self, event):
        if self.join_worker and self.join_worker.isRunning():
            QMessageBox.warning(
                self,
                "Join In Progress",
                "Please wait until the join operation finishes."
            )
            event.ignore()
            return

        super().closeEvent(event)






if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = JoinWindow()
    window.show()

    sys.exit(app.exec())
