
import pandas as pd
import pytest

from data_types import apply_column_types


def test_numeric_conversion():
    df = pd.DataFrame({
        "price": ["16.99", "25.50", "10.00"]
    })

    result = apply_column_types(
        df, {"price": "number"}
    )

    assert pd.api.types.is_numeric_dtype(result["price"])
    assert result["price"].tolist() == [16.99, 25.50, 10.0]


def test_preserve_leading_zeros():
    df = pd.DataFrame({
        "customer_id": ["00123", "00045"]
    })

    result = apply_column_types(
        df, {"customer_id": "text"}
    )

    assert result["customer_id"].tolist() == [
        "00123", "00045"
    ]


def test_invalid_number():
    df = pd.DataFrame({
        "price": ["10.50", "invalid", "20.00"]
    })

    with pytest.raises(ValueError):
        apply_column_types(
            df, {"price": "number"}
        )


def test_missing_numeric_values():
    df = pd.DataFrame({
        "price": ["10.50", "", None]
    })

    result = apply_column_types(
        df, {"price": "number"}
    )

    assert result["price"].iloc[0] == 10.50
    assert pd.isna(result["price"].iloc[1])
    assert pd.isna(result["price"].iloc[2])


def test_original_data_unchanged():
    df = pd.DataFrame({
        "price": ["10.50", "20.00"]
    })

    original = df.copy(deep=True)

    apply_column_types(
        df, {"price": "number"}
    )

    pd.testing.assert_frame_equal(df, original)




def test_unselected_columns_unchanged():
    df = pd.DataFrame({
        "price": ["12.50", "20.00"],
        "invoice_number": ["000123", "000456"]
    })

    result = apply_column_types(
        df,
        {"price": "number"}
    )

    assert pd.api.types.is_numeric_dtype(result["price"])

    assert result["invoice_number"].tolist() == [
        "000123", "000456"
    ]


def test_unknown_column_rejected():
    df = pd.DataFrame({
        "price": ["10.50"]
    })

    with pytest.raises(ValueError):
        apply_column_types(
            df,
            {"missing_column": "number"}
        )
