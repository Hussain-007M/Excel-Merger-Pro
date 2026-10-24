
import pandas as pd

from type_suggestions import suggest_column_types


def test_decimal_numbers():
    df = pd.DataFrame({
        "price": ["12.50", "25.75", "100.00"]
    })

    result = suggest_column_types(df)

    assert result["price"] == "Number"


def test_leading_zeros():
    df = pd.DataFrame({
        "customer_id": ["00123", "00456"]
    })

    result = suggest_column_types(df)

    assert result["customer_id"] == "Keep Original"


def test_integer_values():
    df = pd.DataFrame({
        "quantity": ["10", "20", "30"]
    })

    result = suggest_column_types(df)

    assert result["quantity"] == "Keep Original"


def test_mixed_values():
    df = pd.DataFrame({
        "product": ["12.50", "ABC123", "30.00"]
    })

    result = suggest_column_types(df)

    assert result["product"] == "Keep Original"


def test_empty_values():
    df = pd.DataFrame({
        "price": ["", None, ""]
    })

    result = suggest_column_types(df)

    assert result["price"] == "Keep Original"


def test_original_data_not_modified():
    df = pd.DataFrame({
        "price": ["12.50", "25.75"]
    })

    original = df.copy(deep=True)

    suggest_column_types(df)

    pd.testing.assert_frame_equal(df, original)



def test_decimal_identifier_protected():
    df = pd.DataFrame({
        "invoice_id": ["123.50", "456.75"]
    })

    result = suggest_column_types(df)

    assert result["invoice_id"] == "Keep Original"


def test_product_code_protected():
    df = pd.DataFrame({
        "product_code": ["12.50", "15.75"]
    })

    result = suggest_column_types(df)

    assert result["product_code"] == "Keep Original"


def test_decimal_leading_zeros_protected():
    df = pd.DataFrame({
        "reference": ["001.50", "002.75"]
    })

    result = suggest_column_types(df)

    assert result["reference"] == "Keep Original"
