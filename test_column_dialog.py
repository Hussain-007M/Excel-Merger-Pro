import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMessageBox,
    QDialog,
)

from universal_merge import (
    inspect_sources,
    list_input_files,
    read_file,
)

from type_suggestions import suggest_column_types
from column_types_dialog import ColumnTypesDialog


app = QApplication(sys.argv)

folder = QFileDialog.getExistingDirectory(
    None,
    "Choose Folder Containing CSV or Excel Files"
)

if folder:
    try:
        sources = inspect_sources(Path(folder))

        if not sources:
            raise ValueError("No CSV or XLSX files found.")

        # Collect real column names from all files
        columns = list(dict.fromkeys(
            column
            for file_columns in sources.values()
            for column in file_columns
        ))

        
        # Collect suggestions from real source files
        file_suggestions = []

        for path in list_input_files(Path(folder)):
            df = read_file(path)

            file_suggestions.append(
                suggest_column_types(df)
            )

        # Conservative agreement across files
        suggestions = {}

        for column in columns:
            votes = [
                result[column]
                for result in file_suggestions
                if column in result
            ]

            if votes and all(
                vote == "Number" for vote in votes
            ):
                suggestions[column] = "Number"
            else:
                suggestions[column] = "Keep Original"


        dialog = ColumnTypesDialog(suggestions)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            print("Selected column types:")
            print(dialog.choices)

    except Exception as error:
        QMessageBox.critical(
            None,
            "Inspection Failed",
            str(error)
        )
