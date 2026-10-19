
import pandas as pd


def apply_column_types(df, column_types):
    """
    Convert columns using explicit user choices.
    Never guess column types automatically.
    """

    result = df.copy()

    for column, data_type in column_types.items():

        if column not in result.columns:
            raise ValueError(
                f"Column not found: {column}"
            )

        if data_type == "text":
            result[column] = result[column].astype("string")

        elif data_type == "number":
            values = result[column].astype("string").str.strip()

            missing = values.isna() | values.eq("")
            converted = pd.to_numeric(
                values.mask(missing),
                errors="coerce"
            )

            invalid = (~missing) & converted.isna()

            if invalid.any():
                raise ValueError(
                    f"Invalid number in column '{column}': "
                    f"{values[invalid].iloc[0]}"
                )

            result[column] = converted

        else:
            raise ValueError(
                f"Unsupported data type: {data_type}"
            )

    return result
