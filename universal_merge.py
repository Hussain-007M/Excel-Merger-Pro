from __future__ import annotations
from data_types import apply_column_types
import argparse
import json
import os
from pathlib import Path

import pandas as pd
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter


# =====================================
# AUTOMATIC COLOR THEMES
# =====================================

SUPPORTED = {".csv", ".xlsx"}
MAX_DATA_ROWS = 1_048_575


# =====================================
# FILE READING
# =====================================

def list_input_files(folder: Path):
    if not folder.is_dir():
        raise ValueError("Input folder does not exist")

    return sorted(
        p for p in folder.iterdir()
        if p.is_file()
        and p.suffix.lower() in SUPPORTED
        and not p.name.startswith("~$")
    )


def read_file(path: Path):
    if path.suffix.lower() == ".csv":
        try:
            df = pd.read_csv(
                path,
                dtype=str,
                encoding="utf-8-sig"
            )
        except UnicodeDecodeError:
            df = pd.read_csv(
                path,
                dtype=str,
                encoding="cp1252"
            )
    else:
        df = pd.read_excel(
            path,
            dtype=str,
            sheet_name=0
        )

    df.columns = [
        str(col).strip()
        for col in df.columns
    ]

    if df.columns.duplicated().any():
        raise ValueError(
            f"Duplicate columns in {path.name}"
        )

    if "Source File" in df.columns:
        raise ValueError(
            f"Reserved column in {path.name}: Source File"
        )

    return df


def inspect_sources(folder: Path):
    return {
        path.name: list(read_file(path).columns)
        for path in list_input_files(folder)
    }


# =====================================
# RANDOM COLOR SELECTION
# =====================================
# =====================================
# EXCEL FORMATTING
# =====================================


def style_sheet(ws):
    ws.sheet_view.zoomScale = 90

    # Row heights
    ws.sheet_format.defaultRowHeight = 26
    ws.row_dimensions[1].height = 42

    # Header formatting without colors
    for cell in ws[1]:
        cell.font = Font(
            name="Aptos",
            size=15,
            bold=True
        )

        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True
        )

    # Automatic column widths
    for col_index in range(1, ws.max_column + 1):
        widest = len(str(ws.cell(1, col_index).value or ""))

        for row_index in range(2, min(ws.max_row, 102) + 1):
            value = ws.cell(row_index, col_index).value
            if value is not None:
                widest = max(widest, len(str(value)))

        letter = get_column_letter(col_index)
        ws.column_dimensions[letter].width = min(
            max(widest + 4, 18), 48
        )

    # Data formatting without colors
    data_font = Font(name="Aptos", size=12)
    data_alignment = Alignment(vertical="center")

    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.font = data_font
            cell.alignment = data_alignment

# =====================================
# UNIVERSAL MERGE ENGINE
# =====================================

def merge_files(
    input_folder,
    output_folder,
    mapping=None,
    selected=None,
    progress=None,
    column_types=None
):
    source = Path(input_folder).resolve()
    target = Path(output_folder).resolve()

    if source == target:
        raise ValueError(
            "Input and output folders must be different"
        )

    files = list_input_files(source)

    if not files:
        raise ValueError(
            "No CSV or XLSX files found"
        )

    target.mkdir(
        parents=True,
        exist_ok=True
    )

    mapping = mapping or {}

    frames = []
    summary = []

    for index, path in enumerate(files, 1):
        if progress:
            progress(
                f"Reading {index}/{len(files)}: {path.name}"
            )

        df = read_file(path)

        original_rows = len(df)

        # Remove completely empty rows
        df = df.dropna(how="all").copy()

        # Column mapping for this file
        file_mapping = mapping.get(
            path.name,
            {}
        )

        renames = {
            column: file_mapping.get(
                column,
                column
            ).strip()
            for column in df.columns
        }

        if any(
            not name
            for name in renames.values()
        ):
            raise ValueError(
                f"Blank mapped column in {path.name}"
            )

        if len(set(renames.values())) != len(renames):
            raise ValueError(
                f"Duplicate mapped columns in {path.name}"
            )

        if "Source File" in renames.values():
            raise ValueError(
                "Source File is a reserved column"
            )

        df.rename(
            columns=renames,
            inplace=True
        )
        print("DEBUG COLUMNS:", list(df.columns))



        # Apply only explicitly approved column types
        requested_types = column_types or {}

        applicable_types = {
            column: data_type
            for column, data_type in requested_types.items()
            if column in df.columns
        }

        if applicable_types:
            df = apply_column_types(
                df,
                applicable_types
            )


        
        df["Source File"] = path.name
        print("DEBUG TYPES:", df.dtypes.to_dict())

        frames.append(df)

        summary.append({
            "Source File": path.name,
            "Original Rows": original_rows,
            "Clean Rows": len(df),
            "Excluded Rows": original_rows - len(df)
        })

    # Merge all sources
    merged = pd.concat(
        frames,
        ignore_index=True,
        sort=False
    )

    # Choose and reorder output columns
    if selected is not None:
        selected = list(
            dict.fromkeys(selected)
        )

        if not selected:
            raise ValueError(
                "Choose at least one column"
            )

        missing = [
            name for name in selected
            if name not in merged.columns
        ]

        if missing:
            raise ValueError(
                "Unknown output columns: "
                + ", ".join(missing)
            )

        merged = merged[selected]

    if len(merged.columns) > 16_384:
        raise ValueError(
            "Excel column limit exceeded"
        )

    if len(merged.columns) == 0:
        raise ValueError(
            "No columns to export"
        )

    # Choose a new color

    report = (
        target / "Universal_Merged.xlsx"
    )

    temporary_report = (
        target / "Universal_Merged_temp.xlsx"
    )

    if progress:
        progress(
            "Writing and styling Excel report..."
        )

    try:
        with pd.ExcelWriter(
            temporary_report,
            engine="openpyxl"
        ) as writer:

            summary_df = pd.DataFrame(
                summary
            )

            summary_df.to_excel(
                writer,
                sheet_name="Merge Summary",
                index=False
            )

            summary_ws = writer.sheets["Merge Summary"]

            summary_ws.column_dimensions["A"].width = 34
            summary_ws.column_dimensions["B"].width = 20
            summary_ws.column_dimensions["C"].width = 20
            summary_ws.column_dimensions["D"].width = 22

            summary_ws.row_dimensions[1].height = 36
            summary_ws.sheet_format.defaultRowHeight = 25

            for cell in summary_ws[1]:
                cell.font = Font(
                    name="Aptos",
                    size=15,
                    bold=True
                )
                cell.alignment = Alignment(
                    horizontal="center",
                    vertical="center",
                    wrap_text=True
                )

                readable_names = {
                "order_id": "Order ID",
                "customer_id": "Customer ID",
                "customer_unique_id": "Unique Customer ID",
                "customer_zip_code_prefix": "Postal Code",
                "customer_city": "Customer City",
                "customer_state": "Customer State",
                "order_status": "Order Status",
                "order_purchase_timestamp": "Purchase Date",
                "order_approved_at": "Approval Date",
                "order_delivered_carrier_date": "Shipped Date",
                "order_delivered_customer_date": "Delivery Date",
                "order_estimated_delivery_date": "Estimated Delivery",
            }

                merged_export = merged.rename(
                columns=lambda name: readable_names.get(
                    name,
                    str(name).replace("_", " ").strip().title()
                )
            )

               # Split data to respect Excel row limit
            if merged.empty:
                merged_export.to_excel(
                    writer,
                    sheet_name="Merged Data 1",
                    index=False
                )
            else:
                for start in range(
                    0,
                    len(merged),
                    MAX_DATA_ROWS
                ):
                    chunk = merged_export.iloc[
                        start:start + MAX_DATA_ROWS
                    ]

                    sheet_number = start // MAX_DATA_ROWS + 1

                    chunk.to_excel(
                        writer,
                        sheet_name=f"Merged Data {sheet_number}",
                        index=False
                    )
                 
                
            # Format every sheet
                        # Apply existing formatting once per sheet
            for ws in writer.book.worksheets:
                if ws.title == "Merge Summary":
                    continue
                style_sheet(ws)

        # Protect previous report on failure
        os.replace(
            temporary_report,
            report
        )

    except Exception:
        try:
            temporary_report.unlink(
                missing_ok=True
            )
        except OSError:
            pass

        raise

    # Remember the successful color

    stats = {
        "files": len(files),
        "original_rows": sum(
            item["Original Rows"]
            for item in summary
        ),
        "clean_rows": len(merged),
        "excluded_rows": sum(
            item["Excluded Rows"]
            for item in summary
        ),
        "report": str(report)
    }

    if progress:
        progress("Merge complete")

    return stats


# =====================================
# COMMAND LINE EXECUTION
# =====================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tabrion v3"
    )

    parser.add_argument(
        "input_folder"
    )

    parser.add_argument(
        "output_folder"
    )

    parser.add_argument(
        "--config",
        help="Optional JSON configuration"
    )

    args = parser.parse_args()

    config = {}

    if args.config:
        config = json.loads(
            Path(args.config).read_text(
                encoding="utf-8"
            )
        )

    result = merge_files(
        args.input_folder,
        args.output_folder,
        mapping=config.get("mapping"),
        selected=config.get("selected"),
        progress=print
    )

    print(
        "SUCCESS:",
        json.dumps(
            result,
            ensure_ascii=False
        )
    )
