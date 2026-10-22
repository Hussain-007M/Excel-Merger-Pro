from pathlib import Path
import pandas as pd
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter


def read_table(path):
    path = Path(path)

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

    elif path.suffix.lower() == ".xlsx":
        df = pd.read_excel(
            path,
            dtype=str
        )

    else:
        raise ValueError("Unsupported file type")

    df.columns = df.columns.astype(str).str.strip()

    if df.columns.duplicated().any():
        raise ValueError("Duplicate column names found")

    return df


def join_tables(
    left_file,
    right_file,
    output_folder,
    join_type="left",
    left_key="customer_id",
    right_key="customer_id",
    readable_ids=False 
):
    if join_type not in ("left", "inner"):
        raise ValueError("Unsupported JOIN type")
    left_df = read_table(left_file,)
    right_df = read_table(right_file)

    

    if left_key not in left_df.columns:
        raise ValueError(
            f"Column '{left_key}' not found in left file"
        )

    if right_key not in right_df.columns:
        raise ValueError(
            f"Column '{right_key}' not found in right file"
        )

    # Prevent accidental row multiplication
    if right_df[right_key].isna().any():
     raise ValueError(
            "Empty values found in the right JOIN column"
        )

    if right_df[right_key].duplicated().any():
        raise ValueError(
            "Duplicate values found in the right JOIN column"
        )

    joined = left_df.merge(
        right_df,
        how=join_type,
        left_on=left_key,
        right_on=right_key,
        validate="many_to_one",
        indicator=True,
        suffixes=("_order", "_customer")
    )

    matched = int(
        (joined["_merge"] == "both").sum()
    )

    unmatched = int(
        (~left_df[left_key].isin(right_df[right_key])).sum()
    )

    joined.drop(
        columns=["_merge"],
        inplace=True
    )

    output_folder = Path(output_folder)
    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = output_folder / "Joined_Data.xlsx"

    # Excel supports up to 1,048,576 rows
    if len(joined) > 1_048_575:
        raise ValueError(
            "Result exceeds Excel worksheet row limit"
        )

    summary = pd.DataFrame([
        {"Metric": "Left File Rows", "Value": len(left_df)},
        {"Metric": "Right File Rows", "Value": len(right_df)},
        {"Metric": "Matched Rows", "Value": matched},
        {"Metric": "Unmatched Left Rows", "Value": unmatched},
        {"Metric": "Joined Rows", "Value": len(joined)}
    ])

    
    
    readable_names = {
        "order_id": "Order ID",
        "customer_id": "Customer ID",
        "order_status": "Order Status",
        "order_purchase_timestamp": "Purchase Date",
        "order_approved_at": "Approval Date",
        "order_delivered_carrier_date": "Shipped Date",
        "order_delivered_customer_date": "Delivery Date",
        "order_estimated_delivery_date": "Estimated Delivery",
        "customer_unique_id": "Unique Customer ID",
        "customer_zip_code_prefix": "Postal Code",
        "customer_city": "Customer City",
        "customer_state": "Customer State",
    }

    joined_export = joined.copy()

    if readable_ids:
        for column, prefix, new_name in [
            ("order_id", "ORD", "Order No."),
            ("customer_id", "CUS", "Customer No.")
        ]:
            if column in joined.columns:
                unique_ids = joined[column].dropna().unique()

                id_mapping = {
                    value: f"{prefix}-{i:04d}"
                    for i, value in enumerate(unique_ids, start=1)
                }

                joined_export.insert(
                    0,
                    new_name,
                    joined[column].map(id_mapping)
                )

    
    
    with pd.ExcelWriter(
        output_file,
        engine="openpyxl"
    ) as writer:
        summary.to_excel(
            writer,
            sheet_name="Join Summary",
            index=False
        )

        summary_ws = writer.sheets["Join Summary"]

        summary_ws.column_dimensions["A"].width = 30
        summary_ws.column_dimensions["B"].width = 18

        summary_ws.row_dimensions[1].height = 32

        for cell in summary_ws[1]:
            cell.font = Font(name="Aptos", size=15, bold=True)
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center"
            )

        for row in summary_ws.iter_rows(min_row=2):
            for cell in row:
                cell.font = Font(name="Aptos", size=13)

        summary_ws.sheet_format.defaultRowHeight = 24

        joined_export.to_excel(
            writer,
            sheet_name="Joined Data",
            index=False
        )

        ws = writer.sheets["Joined Data"]
                # Hide original IDs when Readable IDs is enabled
        if readable_ids:
            for column_name in ["Order ID", "Customer ID", "Unique Customer ID"]:
                if column_name in joined_export.columns:
                    col_index = joined_export.columns.get_loc(column_name) + 1
                    col_letter = get_column_letter(col_index)
                    ws.column_dimensions[col_letter].hidden = True


        
        
        # Format headers
        ws.row_dimensions[1].height = 26

        for cell in ws[1]:
            cell.font = Font(
                name="Aptos",
                size=11,
                bold=True
            )
            cell.alignment = Alignment(
                horizontal="left",
                vertical="center",
                wrap_text=False
            )

        # Format data
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.font = Font(
                    name="Aptos",
                    size=11
                )
                cell.alignment = Alignment(
                    vertical="center"
                )

        ws.sheet_format.defaultRowHeight = 20


        
        # Adjust column widths
       
        # Adjust column widths without changing data
        for col_index, col_name in enumerate(
            joined_export.columns, start=1
        ):
            letter = get_column_letter(col_index)
            name = str(col_name)

            if "id" in name.lower():
                width = 40
            else:
                width = min(
                    max(len(name) + 3, 16),
                    40
                )

            ws.column_dimensions[letter].width = width


