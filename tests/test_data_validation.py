"""
StudentPulse — Automated Test Suite
Module: test_data_validation.py
Author: Daniel Richard Xavier

Unit tests for CSV loading, inspection, role detection, data validation,
and non-destructive dataset cleaning.
"""

import io
import os
import pandas as pd
import pytest

from src.data_validation import (
    load_dataset,
    inspect_dataframe,
    detect_column_roles,
    validate_dataset,
    clean_dataset,
)


@pytest.fixture
def sample_csv_path():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_students.csv")
    return os.path.abspath(path)


@pytest.fixture
def valid_dataframe():
    return pd.DataFrame({
        "student_id": ["S1", "S2", "S3", "S4"],
        "student_name": ["Alice", "Bob", "Charlie", "Diana"],
        "subject": ["Math", "Math", "Science", "Science"],
        "semester": ["Sem 1", "Sem 1", "Sem 1", "Sem 1"],
        "class_section": ["CS-A", "CS-A", "CS-B", "CS-B"],
        "marks": [85.0, 72.5, 45.0, 32.0],
        "attendance_percentage": [92.0, 80.0, 74.0, 60.0],
    })


def test_load_dataset_valid_file(sample_csv_path):
    df, err = load_dataset(sample_csv_path)
    assert err is None
    assert df is not None
    assert not df.empty
    assert len(df) > 50
    assert "marks" in df.columns
    assert "attendance_percentage" in df.columns


def test_load_dataset_from_buffer(valid_dataframe):
    csv_buf = io.StringIO(valid_dataframe.to_csv(index=False))
    df, err = load_dataset(csv_buf)
    assert err is None
    assert df is not None
    assert len(df) == 4


def test_load_dataset_empty_csv():
    empty_buf = io.StringIO("")
    df, err = load_dataset(empty_buf)
    assert df is None
    assert err is not None
    assert "empty" in err.lower()


def test_load_dataset_none():
    df, err = load_dataset(None)
    assert df is None
    assert "no data source" in err.lower()


def test_inspect_dataframe(valid_dataframe):
    info = inspect_dataframe(valid_dataframe)
    assert info["total_rows"] == 4
    assert info["total_columns"] == 7
    assert info["missing_total"] == 0
    assert info["duplicate_rows"] == 0
    assert "marks" in info["columns"]


def test_detect_column_roles(valid_dataframe):
    roles = detect_column_roles(valid_dataframe)
    assert roles["student_id"] == "student_id"
    assert roles["student_name"] == "student_name"
    assert roles["marks"] == "marks"
    assert roles["attendance"] == "attendance_percentage"
    assert roles["subject"] == "subject"
    assert roles["semester"] == "semester"
    assert roles["class_section"] == "class_section"


def test_validate_dataset_all_valid(valid_dataframe):
    roles = detect_column_roles(valid_dataframe)
    report = validate_dataset(valid_dataframe, roles)
    assert report["is_valid"] is True
    assert len(report["errors"]) == 0


def test_validate_dataset_missing_marks_column(valid_dataframe):
    df_no_marks = valid_dataframe.drop(columns=["marks"])
    roles = {"marks": "marks"}
    report = validate_dataset(df_no_marks, roles)
    assert report["is_valid"] is False
    assert any("marks" in err.lower() for err in report["errors"])


def test_validate_dataset_non_numeric_marks():
    df = pd.DataFrame({
        "student_id": ["S1", "S2"],
        "marks": ["invalid", "corrupted"],
    })
    roles = {"marks": "marks"}
    report = validate_dataset(df, roles)
    assert report["is_valid"] is False
    assert any("numeric" in err.lower() for err in report["errors"])


def test_validate_dataset_with_warnings():
    df = pd.DataFrame({
        "student_id": ["S1", "S1"],  # duplicate row
        "marks": [115.0, 115.0],      # out of 0-100 bounds
        "attendance": [105.0, 105.0], # out of 0-100 bounds
    })
    roles = {"student_id": "student_id", "marks": "marks", "attendance": "attendance"}
    report = validate_dataset(df, roles)
    assert report["is_valid"] is True  # Non-blocking warnings
    assert len(report["warnings"]) >= 2


def test_clean_dataset_removes_duplicates():
    df = pd.DataFrame({
        "student_id": ["S1", "S1", "S2"],
        "marks": [75.0, 75.0, 85.0],
    })
    roles = {"marks": "marks"}
    cleaned, log = clean_dataset(df, roles, drop_duplicates=True)
    assert len(cleaned) == 2
    assert len(df) == 3  # Original not mutated
    assert any("duplicate" in item.lower() for item in log)


def test_clean_dataset_clips_out_of_bounds_values():
    df = pd.DataFrame({
        "student_id": ["S1", "S2", "S3"],
        "marks": [-10.0, 80.0, 150.0],
        "attendance": [-5.0, 90.0, 110.0],
    })
    roles = {"marks": "marks", "attendance": "attendance"}
    cleaned, log = clean_dataset(df, roles, clip_ranges=True)
    assert cleaned["marks"].min() == 0.0
    assert cleaned["marks"].max() == 100.0
    assert cleaned["attendance"].min() == 0.0
    assert cleaned["attendance"].max() == 100.0
    assert df["marks"].min() == -10.0  # Original not mutated
