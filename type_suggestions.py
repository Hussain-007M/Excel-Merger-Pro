
import re

import pandas as pd



import re

import pandas as pd


def suggest_column_types(df):
    """
    Suggest numeric columns conservatively.
    Never modify the original DataFrame.
    """

    suggestions = {}

    protected_words = {
        "id", "code", "phone", "mobile",
        "zip", "postal", "sku", "account",
        "invoice", "reference", "ref",
        "serial", "barcode", "identifier"
    }

    for column in df.columns:
        suggestion = "Keep Original"

        # Protect identifiers based on column names
        name_parts = set(
            re.findall(
                r"[a-z0-9]+",
                str(column).casefold()
            )
        )

        if name_parts & protected_words:
            suggestions[column] = suggestion
            continue

        values = (
            df[column]
            .dropna()
            .astype("string")
            .str.strip()
        )

        values = values[
            values.notna() & values.ne("")
        ]

        if values.empty:
            suggestions[column] = suggestion
            continue

        # Protect identifiers with leading zeros
        has_leading_zeros = values.str.fullmatch(
            r"[+-]?0\d+(?:\.\d+)?"
        ).any()

        if has_leading_zeros:
            suggestions[column] = suggestion
            continue

        numeric_values = pd.to_numeric(
            values,
            errors="coerce"
        )

        all_numeric = numeric_values.notna().all()

        # Suggest Number for standard decimal values
        has_decimals = values.str.fullmatch(
            r"[+-]?\d+\.\d+"
        ).any()

        if all_numeric and has_decimals:
            suggestion = "Number"

        suggestions[column] = suggestion

    return suggestions
