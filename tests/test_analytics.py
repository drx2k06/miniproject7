"""
StudentPulse — Automated Test Suite
Module: test_analytics.py
Author: Daniel Richard Xavier

Unit tests for analytical aggregations, metric derivations, pass-rate thresholds,
academic support rule boundaries, and filtering mechanics.
"""

import os
import pandas as pd
import pytest

from src.analytics import (
    categorize_performance,
    calculate_overview_metrics,
    flag_academic_support,
    get_subject_statistics,
    get_attendance_correlation,
    get_tier_distribution,
    filter_dataset,
    ETHICAL_DISCLAIMER,
    CORRELATION_DISCLAIMER,
)
from src.data_validation import load_dataset, detect_column_roles


@pytest.fixture
def analytics_sample_df():
    return pd.DataFrame({
        "student_id": ["S101", "S101", "S102", "S102", "S103", "S104"],
        "subject": ["Math", "Physics", "Math", "Physics", "Math", "Physics"],
        "semester": ["Sem 1", "Sem 1", "Sem 1", "Sem 1", "Sem 2", "Sem 2"],
        "class_section": ["CS-A", "CS-A", "CS-A", "CS-A", "CS-B", "CS-B"],
        "marks": [90.0, 85.0, 55.0, 48.0, 35.0, 72.0],
        "attendance": [95.0, 90.0, 80.0, 70.0, 50.0, 88.0],
    })


def test_categorize_performance():
    assert "Distinction" in categorize_performance(95.0)
    assert "Distinction" in categorize_performance(75.0)
    assert "First Class" in categorize_performance(74.9)
    assert "First Class" in categorize_performance(60.0)
    assert "Second Class" in categorize_performance(59.9)
    assert "Second Class" in categorize_performance(50.0)
    assert "Pass Class" in categorize_performance(49.9)
    assert "Pass Class" in categorize_performance(40.0)
    assert "Remedial" in categorize_performance(39.9)
    assert "Remedial" in categorize_performance(0.0)
    assert categorize_performance(None) == "Not Recorded"


def test_calculate_overview_metrics(analytics_sample_df):
    metrics = calculate_overview_metrics(
        df=analytics_sample_df,
        marks_col="marks",
        attendance_col="attendance",
        student_id_col="student_id",
        pass_threshold=40.0,
        score_support_threshold=45.0,
        attendance_support_threshold=75.0,
    )

    assert metrics["total_records"] == 6
    assert metrics["total_students"] == 4  # S101, S102, S103, S104
    # Mean marks: (90+85+55+48+35+72) / 6 = 385 / 6 = 64.17
    assert metrics["average_score"] == pytest.approx(64.17, rel=1e-2)
    # Mean attendance: (95+90+80+70+50+88) / 6 = 473 / 6 = 78.83
    assert metrics["average_attendance"] == pytest.approx(78.83, rel=1e-2)
    # Passed >= 40: 5 out of 6 -> 83.33%
    assert metrics["passed_records"] == 5
    assert metrics["failed_records"] == 1
    assert metrics["pass_percentage"] == pytest.approx(83.33, rel=1e-2)
    assert metrics["has_attendance"] is True


def test_calculate_overview_metrics_pass_rate_extremes(analytics_sample_df):
    # Pass threshold 100: 0 passed
    m_high = calculate_overview_metrics(
        df=analytics_sample_df,
        marks_col="marks",
        pass_threshold=100.0,
    )
    assert m_high["pass_percentage"] == 0.0
    assert m_high["passed_records"] == 0
    assert m_high["failed_records"] == 6

    # Pass threshold 0: 100% passed
    m_low = calculate_overview_metrics(
        df=analytics_sample_df,
        marks_col="marks",
        pass_threshold=0.0,
    )
    assert m_low["pass_percentage"] == 100.0
    assert m_low["passed_records"] == 6
    assert m_low["failed_records"] == 0


def test_calculate_overview_metrics_empty():
    empty_df = pd.DataFrame()
    metrics = calculate_overview_metrics(empty_df, marks_col="marks")
    assert metrics["total_records"] == 0
    assert metrics["total_students"] == 0
    assert metrics["average_score"] is None
    assert metrics["pass_percentage"] is None


def test_flag_academic_support_boundaries():
    df = pd.DataFrame({
        "student_id": ["A", "B", "C", "D"],
        "marks": [35.0, 42.0, 80.0, 85.0],
        "attendance": [60.0, 85.0, 65.0, 92.0],
    })

    flagged = flag_academic_support(
        df=df,
        marks_col="marks",
        attendance_col="attendance",
        score_threshold=45.0,
        attendance_threshold=75.0,
    )

    # Student A: marks 35 (<45) and att 60 (<75) -> Low Marks & Low Attendance
    assert bool(flagged.loc[0, "Needs_Support"]) is True
    assert "Low Marks" in flagged.loc[0, "Support_Reason"] and "Low Attendance" in flagged.loc[0, "Support_Reason"]

    # Student B: marks 42 (<45) and att 85 (>=75) -> Low Marks only
    assert bool(flagged.loc[1, "Needs_Support"]) is True
    assert "Low Marks" in flagged.loc[1, "Support_Reason"]
    assert "Low Attendance" not in flagged.loc[1, "Support_Reason"]

    # Student C: marks 80 (>=45) and att 65 (<75) -> Low Attendance only
    assert bool(flagged.loc[2, "Needs_Support"]) is True
    assert "Low Attendance" in flagged.loc[2, "Support_Reason"]
    assert "Low Marks" not in flagged.loc[2, "Support_Reason"]

    # Student D: marks 85 (>=45) and att 92 (>=75) -> Satisfactory
    assert bool(flagged.loc[3, "Needs_Support"]) is False
    assert flagged.loc[3, "Support_Reason"] == "Satisfactory"


def test_flag_academic_support_without_attendance():
    df = pd.DataFrame({
        "student_id": ["A", "B"],
        "marks": [38.0, 78.0],
    })

    flagged = flag_academic_support(
        df=df,
        marks_col="marks",
        attendance_col=None,
        score_threshold=45.0,
    )

    assert bool(flagged.loc[0, "Needs_Support"]) is True
    assert "Low Marks" in flagged.loc[0, "Support_Reason"]
    assert bool(flagged.loc[1, "Needs_Support"]) is False
    assert flagged.loc[1, "Support_Reason"] == "Satisfactory"


def test_get_subject_statistics(analytics_sample_df):
    stats = get_subject_statistics(analytics_sample_df, subject_col="subject", marks_col="marks")
    assert len(stats) == 2  # Math and Physics
    assert "Average_Marks" in stats.columns
    assert "Min_Marks" in stats.columns
    assert "Max_Marks" in stats.columns
    assert "Record_Count" in stats.columns
    # Math marks: 90, 55, 35 -> Mean 60.0
    math_row = stats[stats["Subject"] == "Math"].iloc[0]
    assert math_row["Average_Marks"] == 60.0
    assert math_row["Min_Marks"] == 35.0
    assert math_row["Max_Marks"] == 90.0
    assert math_row["Record_Count"] == 3


def test_get_attendance_correlation(analytics_sample_df):
    result = get_attendance_correlation(analytics_sample_df, marks_col="marks", attendance_col="attendance")
    assert result["correlation"] is not None
    assert result["data_points"] == 6
    assert result["disclaimer"] == CORRELATION_DISCLAIMER
    assert isinstance(result["correlation"], float)


def test_get_tier_distribution(analytics_sample_df):
    tiers = get_tier_distribution(analytics_sample_df, marks_col="marks")
    assert len(tiers) == 5
    assert "Tier" in tiers.columns
    assert "Count" in tiers.columns
    assert "Percentage" in tiers.columns
    assert tiers["Count"].sum() == 6


def test_filter_dataset(analytics_sample_df):
    filters = {
        "role_mapping": {
            "subject": "subject",
            "semester": "semester",
            "class_section": "class_section",
            "marks": "marks",
            "attendance": "attendance",
        },
        "subjects": ["Math"],
        "semesters": ["Sem 1"],
        "classes": ["CS-A"],
        "marks_range": (50.0, 100.0),
        "attendance_range": (70.0, 100.0),
    }

    filtered = filter_dataset(analytics_sample_df, filters)
    assert len(filtered) == 2  # S101 (90) and S102 (55)
    assert all(filtered["subject"] == "Math")
    assert all(filtered["semester"] == "Sem 1")


def test_sample_dataset_end_to_end():
    sample_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_students.csv")
    df, err = load_dataset(sample_path)
    assert err is None
    assert df is not None

    roles = detect_column_roles(df)
    metrics = calculate_overview_metrics(
        df=df,
        marks_col=roles["marks"],
        attendance_col=roles["attendance"],
        student_id_col=roles["student_id"],
        pass_threshold=40.0,
    )

    assert metrics["total_students"] > 10
    assert metrics["average_score"] > 50.0
    assert metrics["average_attendance"] > 70.0
    assert metrics["pass_percentage"] > 70.0
