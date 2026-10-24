
import pandas as pd
import pytest

from join_engine import join_tables


@pytest.fixture
def sample_files(tmp_path):
    left_file = tmp_path / "orders.csv"
    right_file = tmp_path / "customers.csv"
    output_folder = tmp_path / "output"

    orders = pd.DataFrame({
        "order_id": ["ORD001", "ORD002", "ORD003"],
        "customer_id": ["001", "002", "999"],
        "amount": ["100", "200", "300"]
    })

    customers = pd.DataFrame({
        "customer_id": ["001", "002"],
        "customer_name": ["Ahmed", "Sara"]
    })

    orders.to_csv(left_file, index=False)
    customers.to_csv(right_file, index=False)

    return left_file, right_file, output_folder


def read_result(output_folder):
    report = output_folder / "Joined_Data.xlsx"

    assert report.exists()

    result = pd.read_excel(
        report,
        sheet_name="Joined Data",
        dtype=str
    )

    summary = pd.read_excel(
        report,
        sheet_name="Join Summary"
    )

    metrics = dict(zip(summary["Metric"], summary["Value"]))

    return result, metrics


def test_left_join_preserves_all_left_rows(sample_files):
    left_file, right_file, output_folder = sample_files

    join_tables(
        left_file,
        right_file,
        output_folder,
        join_type="left",
        left_key="customer_id",
        right_key="customer_id",
        readable_ids=False
    )

    result, metrics = read_result(output_folder)

    assert len(result) == 3
    assert result["customer_id"].tolist() == [
        "001", "002", "999"
    ]
    assert result["order_id"].tolist() == [
        "ORD001", "ORD002", "ORD003"
    ]

    assert result["customer_name"].iloc[0] == "Ahmed"
    assert result["customer_name"].iloc[1] == "Sara"
    assert pd.isna(result["customer_name"].iloc[2])

    assert metrics["Matched Rows"] == 2
    assert metrics["Unmatched Left Rows"] == 1
    assert metrics["Joined Rows"] == 3


def test_inner_join_excludes_unmatched_rows(sample_files):
    left_file, right_file, output_folder = sample_files

    join_tables(
        left_file,
        right_file,
        output_folder,
        join_type="inner",
        left_key="customer_id",
        right_key="customer_id"
    )

    result, metrics = read_result(output_folder)

    assert len(result) == 2
    assert result["customer_id"].tolist() == [
        "001", "002"
    ]
    assert metrics["Joined Rows"] == 2
    assert metrics["Unmatched Left Rows"] == 1


def test_duplicate_right_keys_are_rejected(tmp_path):
    left_file = tmp_path / "left.csv"
    right_file = tmp_path / "right.csv"

    pd.DataFrame({
        "customer_id": ["001"]
    }).to_csv(left_file, index=False)

    pd.DataFrame({
        "customer_id": ["001", "001"]
    }).to_csv(right_file, index=False)

    with pytest.raises(ValueError, match="Duplicate values"):
        join_tables(
            left_file,
            right_file,
            tmp_path / "output",
            left_key="customer_id",
            right_key="customer_id"
        )


def test_join_does_not_modify_input_files(sample_files):
    left_file, right_file, output_folder = sample_files

    original_left = left_file.read_bytes()
    original_right = right_file.read_bytes()

    join_tables(
        left_file,
        right_file,
        output_folder,
        left_key="customer_id",
        right_key="customer_id"
    )

    assert left_file.read_bytes() == original_left
    assert right_file.read_bytes() == original_right
