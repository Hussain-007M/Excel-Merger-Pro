
import sys

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHeaderView,
)


class ColumnTypesDialog(QDialog):
    def __init__(self, suggestions):
        super().__init__()

        self.suggestions = suggestions
        self.choices = {}

        self.setWindowTitle("Tabrion | Column Types")
        self.resize(760, 520)

        self.setStyleSheet("""
            QDialog {
                background-color: #10111B;
            }

            QLabel {
                color: #F4F4FA;
                font-family: "Segoe UI";
            }

            QTableWidget {
                background-color: #1B1D2B;
                color: white;
                border: none;
                gridline-color: #34374A;
                font-size: 13px;
            }

            QHeaderView::section {
                background-color: #292C40;
                color: white;
                padding: 10px;
                border: none;
            }

            QComboBox {
                background-color: #292C40;
                color: white;
                border-radius: 6px;
                padding: 7px;
            }

            QComboBox QAbstractItemView {
                background-color: #292C40;
                color: white;
                selection-background-color: #8B5CF6;
            }

            QPushButton {
                background-color: #292C40;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 11px 16px;
            }

            QPushButton:hover {
                background-color: #383B57;
            }

            QPushButton#primary {
                background-color: #8B5CF6;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(16)

        title = QLabel("Column Type Settings")
        title.setStyleSheet(
            "font-size: 25px; font-weight: bold;"
        )

        description = QLabel(
            "Review suggested types before applying changes."
        )
        description.setStyleSheet("color: #A5A8BD;")

        layout.addWidget(title)
        layout.addWidget(description)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            "Column",
            "Suggested Type",
            "Your Choice"
        ])

        self.table.setRowCount(len(suggestions))
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.selectors = {}

        for row, (column, suggestion) in enumerate(
            suggestions.items()
        ):
            column_item = QTableWidgetItem(column)
            suggestion_item = QTableWidgetItem(suggestion)

            self.table.setItem(row, 0, column_item)
            self.table.setItem(row, 1, suggestion_item)

            selector = QComboBox()
            selector.addItems([
                "Keep Original",
                "Text",
                "Number"
            ])

            self.table.setCellWidget(row, 2, selector)
            self.selectors[column] = selector

        layout.addWidget(self.table)

        actions = QHBoxLayout()

        suggest_button = QPushButton("Use Suggestions")
        suggest_button.clicked.connect(
            self.use_suggestions
        )

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        apply_button = QPushButton("Apply Choices")
        apply_button.setObjectName("primary")
        apply_button.clicked.connect(self.apply_choices)

        actions.addWidget(suggest_button)
        actions.addStretch()
        actions.addWidget(cancel_button)
        actions.addWidget(apply_button)

        layout.addLayout(actions)

    def use_suggestions(self):
        for column, suggestion in self.suggestions.items():
            if suggestion in ("Text", "Number"):
                self.selectors[column].setCurrentText(
                    suggestion
                )

    def apply_choices(self):
        self.choices = {
            column: selector.currentText()
            for column, selector in self.selectors.items()
        }

        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Example suggestions for testing the interface
    sample_suggestions = {
        "total_bill": "Number",
        "tip": "Number",
        "customer_id": "Text",
        "product_code": "Text",
        "size": "Number"
    }

    dialog = ColumnTypesDialog(sample_suggestions)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        print("User choices:")
        print(dialog.choices)

    sys.exit(0)
