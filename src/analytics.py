"""
StudentPulse — Student Performance Analytics Dashboard
Module: analytics.py
Author: Daniel Richard Xavier

Core analytics engine providing robust calculations for student metrics,
performance tier categorization, academic support indicators,
correlation analysis, and multi-dimensional aggregations.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


# Explicit pedagogical disclaimer for academic support indicators
ETHICAL_DISCLAIMER = (
    "Notice: Academic support indicators are rule-based heuristic guidance flags. "
    "They are designed strictly to facilitate early faculty mentoring, peer tutoring, "
    "and counseling. They do not represent automated punitive grading, psychological profiling, "
    "or definitive predictions."
)

CORRELATION_DISCLAIMER = (
    "Statistical Note: Correlation between attendance and marks reflects co-variation in the dataset "
    "and does NOT imply direct mathematical causation. Extraneous factors (prior subject mastery, "
    "study habits, course difficulty) influence academic outcomes."
)


def categorize_performance(score: float) -> str:
    """
    Map an academic percentage score to a recognized tier category.
    """
    if pd.isna(score):
        return "Not Recorded"
    val = float(score)
    if val >= 75.0:
        return "Distinction (>= 75%)"
    elif val >= 60.0:
        return "First Class (60–74%)"
    elif val >= 50.0:
        return "Second Class (50–59%)"
    elif val >= 40.0:
        return "Pass Class (40–49%)"
    else:
        return "Remedial (< 40%)"


def calculate_overview_metrics(
    df: pd.DataFrame,
    marks_col: Optional[str],
    attendance_col: Optional[str] = None,
    student_id_col: Optional[str] = None,
    pass_threshold: float = 40.0,
    score_support_threshold: float = 45.0,
    attendance_support_threshold: float = 75.0,
) -> Dict[str, Any]:
    """
    Calculate high-level summary metrics from the active dataset.
    All metrics are computed dynamically from actual loaded records.
    Never returns hardcoded statistics.
    """
    if df is None or df.empty:
        return {
            "total_records": 0,
            "total_students": 0,
            "average_score": None,
            "median_score": None,
            "min_score": None,
            "max_score": None,
            "average_attendance": None,
            "pass_percentage": None,
            "passed_records": 0,
            "failed_records": 0,
            "support_needed_count": 0,
            "support_needed_percentage": 0.0,
            "has_attendance": False,
        }

    total_records = len(df)
    
    # Calculate unique student count if identifier exists
    if student_id_col and student_id_col in df.columns:
        total_students = int(df[student_id_col].nunique(dropna=True))
    else:
        total_students = total_records

    # Score metrics
    average_score: Optional[float] = None
    median_score: Optional[float] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    pass_percentage: Optional[float] = None
    passed_records = 0
    failed_records = 0

    if marks_col and marks_col in df.columns:
        valid_marks = pd.to_numeric(df[marks_col], errors="coerce").dropna()
        if not valid_marks.empty:
            average_score = round(float(valid_marks.mean()), 2)
            median_score = round(float(valid_marks.median()), 2)
            min_score = round(float(valid_marks.min()), 2)
            max_score = round(float(valid_marks.max()), 2)

            passed_records = int((valid_marks >= pass_threshold).sum())
            failed_records = int((valid_marks < pass_threshold).sum())
            pass_percentage = round((passed_records / len(valid_marks)) * 100.0, 2)

    # Attendance metrics
    average_attendance: Optional[float] = None
    has_attendance = False
    if attendance_col and attendance_col in df.columns:
        valid_att = pd.to_numeric(df[attendance_col], errors="coerce").dropna()
        if not valid_att.empty:
            average_attendance = round(float(valid_att.mean()), 2)
            has_attendance = True

    # Support alert indicators calculation
    flagged_df = flag_academic_support(
        df=df,
        marks_col=marks_col,
        attendance_col=attendance_col,
        student_id_col=student_id_col,
        score_threshold=score_support_threshold,
        attendance_threshold=attendance_support_threshold,
    )
    
    if student_id_col and student_id_col in flagged_df.columns:
        # Count unique students who received any flag
        flagged_students = flagged_df[flagged_df["Needs_Support"]][student_id_col].nunique()
        support_count = int(flagged_students)
        denom = max(total_students, 1)
        support_percentage = round((support_count / denom) * 100.0, 2)
    else:
        support_count = int(flagged_df["Needs_Support"].sum())
        support_percentage = round((support_count / max(total_records, 1)) * 100.0, 2)

    return {
        "total_records": total_records,
        "total_students": total_students,
        "average_score": average_score,
        "median_score": median_score,
        "min_score": min_score,
        "max_score": max_score,
        "average_attendance": average_attendance,
        "pass_percentage": pass_percentage,
        "passed_records": passed_records,
        "failed_records": failed_records,
        "support_needed_count": support_count,
        "support_needed_percentage": support_percentage,
        "has_attendance": has_attendance,
    }


def flag_academic_support(
    df: pd.DataFrame,
    marks_col: Optional[str],
    attendance_col: Optional[str] = None,
    student_id_col: Optional[str] = None,
    score_threshold: float = 45.0,
    attendance_threshold: float = 75.0,
) -> pd.DataFrame:
    """
    Evaluate transparent, configurable rules to identify records or students
    who may benefit from additional academic counseling or tutoring.

    Rules:
    - If score < score_threshold AND attendance < attendance_threshold: Dual Risk
    - If score < score_threshold: Low Academic Score
    - If attendance < attendance_threshold: Low Attendance Warning
    - Otherwise: Satisfactory / On Track
    """
    if df is None or df.empty:
        res = pd.DataFrame()
        res["Needs_Support"] = pd.Series(dtype=bool)
        res["Support_Reason"] = pd.Series(dtype=str)
        return res

    result_df = df.copy()

    has_marks = marks_col is not None and marks_col in df.columns
    has_att = attendance_col is not None and attendance_col in df.columns

    scores = pd.to_numeric(result_df[marks_col], errors="coerce") if has_marks else pd.Series(np.nan, index=result_df.index)
    attendance = pd.to_numeric(result_df[attendance_col], errors="coerce") if has_att else pd.Series(np.nan, index=result_df.index)

    reasons: List[str] = []
    flags: List[bool] = []

    for idx in result_df.index:
        sc = scores.loc[idx]
        att = attendance.loc[idx]

        is_low_score = pd.notna(sc) and (sc < score_threshold)
        is_low_att = pd.notna(att) and (att < attendance_threshold)

        if is_low_score and is_low_att:
            reasons.append(f"Low Marks (<{score_threshold}) & Low Attendance (<{attendance_threshold}%)")
            flags.append(True)
        elif is_low_score:
            reasons.append(f"Low Marks (<{score_threshold})")
            flags.append(True)
        elif is_low_att:
            reasons.append(f"Low Attendance (<{attendance_threshold}%)")
            flags.append(True)
        else:
            reasons.append("Satisfactory")
            flags.append(False)

    result_df["Needs_Support"] = flags
    result_df["Support_Reason"] = reasons
    return result_df


def get_subject_statistics(
    df: pd.DataFrame,
    subject_col: str,
    marks_col: str,
) -> pd.DataFrame:
    """
    Compute aggregate performance metrics (average, min, max, count) per subject.
    """
    if df is None or df.empty or subject_col not in df.columns or marks_col not in df.columns:
        return pd.DataFrame(columns=["Subject", "Average_Marks", "Min_Marks", "Max_Marks", "Record_Count"])

    work_df = df[[subject_col, marks_col]].copy()
    work_df[marks_col] = pd.to_numeric(work_df[marks_col], errors="coerce")
    work_df = work_df.dropna(subset=[marks_col])

    if work_df.empty:
        return pd.DataFrame(columns=["Subject", "Average_Marks", "Min_Marks", "Max_Marks", "Record_Count"])

    grouped = work_df.groupby(subject_col)[marks_col].agg(
        Average_Marks="mean",
        Median_Marks="median",
        Min_Marks="min",
        Max_Marks="max",
        Record_Count="count",
    ).reset_index()

    grouped["Average_Marks"] = grouped["Average_Marks"].round(2)
    grouped["Median_Marks"] = grouped["Median_Marks"].round(2)
    grouped = grouped.rename(columns={subject_col: "Subject"})
    return grouped.sort_values(by="Average_Marks", ascending=False)


def get_attendance_correlation(
    df: pd.DataFrame,
    marks_col: str,
    attendance_col: str,
) -> Dict[str, Any]:
    """
    Calculate Pearson correlation coefficient between attendance and marks.
    Returns correlation value, interpretation, and explicit non-causation warning.
    """
    if df is None or df.empty or marks_col not in df.columns or attendance_col not in df.columns:
        return {
            "correlation": None,
            "data_points": 0,
            "strength": "Insufficient data",
            "disclaimer": CORRELATION_DISCLAIMER,
        }

    work_df = df[[marks_col, attendance_col]].copy()
    work_df[marks_col] = pd.to_numeric(work_df[marks_col], errors="coerce")
    work_df[attendance_col] = pd.to_numeric(work_df[attendance_col], errors="coerce")
    clean_pairs = work_df.dropna()

    n = len(clean_pairs)
    if n < 3:
        return {
            "correlation": None,
            "data_points": n,
            "strength": "Insufficient data (minimum 3 records required)",
            "disclaimer": CORRELATION_DISCLAIMER,
        }

    # Check for zero variance
    if clean_pairs[marks_col].std() == 0 or clean_pairs[attendance_col].std() == 0:
        return {
            "correlation": 0.0,
            "data_points": n,
            "strength": "No variation in one or both columns",
            "disclaimer": CORRELATION_DISCLAIMER,
        }

    corr = float(clean_pairs[marks_col].corr(clean_pairs[attendance_col]))
    corr_rounded = round(corr, 3)

    if corr_rounded >= 0.7:
        strength = "Strong positive co-variation"
    elif corr_rounded >= 0.4:
        strength = "Moderate positive co-variation"
    elif corr_rounded > 0.0:
        strength = "Weak positive co-variation"
    elif corr_rounded == 0.0:
        strength = "No linear co-variation"
    else:
        strength = "Negative co-variation"

    return {
        "correlation": corr_rounded,
        "data_points": n,
        "strength": strength,
        "disclaimer": CORRELATION_DISCLAIMER,
    }


def get_tier_distribution(df: pd.DataFrame, marks_col: str) -> pd.DataFrame:
    """
    Categorize all valid marks into academic tiers and summarize counts.
    """
    if df is None or df.empty or marks_col not in df.columns:
        return pd.DataFrame(columns=["Tier", "Count", "Percentage"])

    scores = pd.to_numeric(df[marks_col], errors="coerce").dropna()
    if scores.empty:
        return pd.DataFrame(columns=["Tier", "Count", "Percentage"])

    tiers = scores.apply(categorize_performance)
    counts = tiers.value_counts()
    
    order = [
        "Distinction (>= 75%)",
        "First Class (60–74%)",
        "Second Class (50–59%)",
        "Pass Class (40–49%)",
        "Remedial (< 40%)",
    ]
    
    res = []
    total = len(scores)
    for cat in order:
        c = int(counts.get(cat, 0))
        pct = round((c / total) * 100.0, 2) if total > 0 else 0.0
        res.append({"Tier": cat, "Count": c, "Percentage": pct})

    return pd.DataFrame(res)


def filter_dataset(
    df: pd.DataFrame,
    filters: Dict[str, Any],
) -> pd.DataFrame:
    """
    Apply multi-dimensional filters:
    - subjects: list of selected subjects
    - semesters: list of selected semesters
    - classes: list of selected classes/sections
    - marks_range: tuple of (min_marks, max_marks)
    - attendance_range: tuple of (min_attendance, max_attendance)
    - role_mapping: dict of column mappings
    """
    if df is None or df.empty:
        return pd.DataFrame()

    filtered = df.copy()
    mapping = filters.get("role_mapping", {})

    # Subject filter
    subject_col = mapping.get("subject")
    selected_subjects = filters.get("subjects")
    if subject_col and subject_col in filtered.columns and selected_subjects:
        filtered = filtered[filtered[subject_col].isin(selected_subjects)]

    # Semester filter
    semester_col = mapping.get("semester")
    selected_semesters = filters.get("semesters")
    if semester_col and semester_col in filtered.columns and selected_semesters:
        filtered = filtered[filtered[semester_col].isin(selected_semesters)]

    # Class filter
    class_col = mapping.get("class_section")
    selected_classes = filters.get("classes")
    if class_col and class_col in filtered.columns and selected_classes:
        filtered = filtered[filtered[class_col].isin(selected_classes)]

    # Marks range filter
    marks_col = mapping.get("marks")
    marks_range = filters.get("marks_range")
    if marks_col and marks_col in filtered.columns and marks_range:
        min_m, max_m = marks_range
        numeric_marks = pd.to_numeric(filtered[marks_col], errors="coerce")
        filtered = filtered[(numeric_marks >= min_m) & (numeric_marks <= max_m)]

    # Attendance range filter
    att_col = mapping.get("attendance")
    att_range = filters.get("attendance_range")
    if att_col and att_col in filtered.columns and att_range:
        min_a, max_a = att_range
        numeric_att = pd.to_numeric(filtered[att_col], errors="coerce")
        filtered = filtered[(numeric_att >= min_a) & (numeric_att <= max_a)]

    return filtered
