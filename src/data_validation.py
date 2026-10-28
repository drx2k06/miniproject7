"""
StudentPulse — Student Performance Analytics Dashboard
Module: data_validation.py
Author: Daniel Richard Xavier

Provides robust CSV dataset loading, schema inspection, column role detection,
validation checks, and non-destructive cleaning utilities.
"""

from __future__ import annotations
import io
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd


def load_dataset(source: Union[str, io.BytesIO, io.StringIO]) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load a CSV dataset from a file path or in-memory byte/string buffer.
    Attempts multiple encodings (utf-8, utf-8-sig, latin1) gracefully.

    Returns:
        (DataFrame, None) on success, or (None, error_message) on failure.
    """
    if source is None:
        return None, "No data source was provided."

    encodings_to_try = ["utf-8", "utf-8-sig", "latin1"]

    # If it's a buffer or file path, attempt reading
    for encoding in encodings_to_try:
        try:
            if hasattr(source, "seek"):
                source.seek(0)
            df = pd.read_csv(source, encoding=encoding)
            
            if df.empty:
                return None, "The provided CSV file contains no data (empty table)."
            
            # Trim column names
            df.columns = [str(col).strip() for col in df.columns]
            return df, None
        except UnicodeDecodeError:
            continue
        except pd.errors.EmptyDataError:
            return None, "The uploaded file is empty or contains no parseable columns."
        except pd.errors.ParserError as pe:
            return None, f"Failed to parse CSV format: {str(pe)}"
        except Exception as exc:
            return None, f"Unexpected error reading dataset: {str(exc)}"

    return None, "Could not decode file using supported encodings (UTF-8, Latin-1)."


def inspect_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Inspect a DataFrame and produce structural metadata:
    - total rows and columns
    - detected column data types
    - missing value count and percentage
    - duplicate row count
    """
    if df is None or df.empty:
        return {
            "total_rows": 0,
            "total_columns": 0,
            "columns": [],
            "dtypes": {},
            "missing_per_column": {},
            "missing_total": 0,
            "duplicate_rows": 0,
        }

    total_rows = int(len(df))
    total_cols = int(len(df.columns))
    dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
    missing_series = df.isna().sum()
    missing_dict = {
        col: {
            "count": int(count),
            "percentage": round(float((count / total_rows) * 100), 2) if total_rows > 0 else 0.0,
        }
        for col, count in missing_series.items()
    }
    missing_total = int(missing_series.sum())
    duplicate_rows = int(df.duplicated().sum())

    return {
        "total_rows": total_rows,
        "total_columns": total_cols,
        "columns": list(df.columns),
        "dtypes": dtypes,
        "missing_per_column": missing_dict,
        "missing_total": missing_total,
        "duplicate_rows": duplicate_rows,
    }


def detect_column_roles(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """
    Heuristically suggest column roles from column names and types.
    Roles:
    - student_id: identifier (student_id, roll_no, usn, id, reg_no)
    - student_name: name (name, student_name, full_name)
    - marks: academic scores (marks, score, total_marks, grade_point, percentage)
    - attendance: attendance percentage or counts (attendance, attendance_percentage, attendance_pct, present_pct)
    - subject: course/subject title (subject, course, module, paper)
    - semester: semester or term (semester, sem, term, academic_year)
    - class_section: class or section (class, section, batch, division, branch)
    """
    if df is None or df.empty:
        return {
            "student_id": None,
            "student_name": None,
            "marks": None,
            "attendance": None,
            "subject": None,
            "semester": None,
            "class_section": None,
        }

    cols = list(df.columns)
    cols_lower = {col: col.lower().strip() for col in cols}

    def find_match(keywords: List[str], require_numeric: bool = False) -> Optional[str]:
        # Exact match check first
        for col, low in cols_lower.items():
            if any(kw == low for kw in keywords):
                if require_numeric and not pd.api.types.is_numeric_dtype(df[col]):
                    continue
                return col
        # Substring check
        for col, low in cols_lower.items():
            if any(kw in low for kw in keywords):
                if require_numeric and not pd.api.types.is_numeric_dtype(df[col]):
                    continue
                return col
        return None

    student_id = find_match(["student_id", "roll_no", "rollno", "usn", "reg_no", "regno", "student_code", "id"])
    student_name = find_match(["student_name", "full_name", "candidate_name", "name"])
    
    # Avoid selecting student_id as student_name if it was already selected
    if student_name == student_id:
        student_name = None

    marks = find_match(["marks", "score", "total_marks", "obtained_marks", "final_score", "grade_point", "percentage"], require_numeric=True)
    # If not found with require_numeric, check any numeric column that has plausibly float/int values
    if marks is None:
        numeric_cols = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
        for nc in numeric_cols:
            low = cols_lower[nc]
            if any(kw in low for kw in ["mark", "score", "grade", "exam", "result"]):
                marks = nc
                break

    attendance = find_match(["attendance_percentage", "attendance_pct", "attendance", "attendance_rate", "present_percentage"], require_numeric=True)
    if attendance is None:
        numeric_cols = [c for c in cols if pd.api.types.is_numeric_dtype(df[c]) and c != marks]
        for nc in numeric_cols:
            low = cols_lower[nc]
            if "attend" in low:
                attendance = nc
                break

    subject = find_match(["subject", "course", "subject_name", "course_name", "module", "paper"])
    semester = find_match(["semester", "sem", "term", "academic_year", "year"])
    class_section = find_match(["class_section", "class", "section", "division", "batch", "cohort", "department", "dept"])

    return {
        "student_id": student_id,
        "student_name": student_name,
        "marks": marks,
        "attendance": attendance,
        "subject": subject,
        "semester": semester,
        "class_section": class_section,
    }


def validate_dataset(df: pd.DataFrame, role_mapping: Dict[str, Optional[str]]) -> Dict[str, Any]:
    """
    Validate a dataset against the selected role mappings.
    Returns a dictionary containing:
    - is_valid (bool): whether critical requirements are met
    - errors (list of strings): blocking issues
    - warnings (list of strings): non-blocking data quality notices
    - notes (list of strings): general observations
    """
    errors: List[str] = []
    warnings: List[str] = []
    notes: List[str] = []

    if df is None or df.empty:
        return {
            "is_valid": False,
            "errors": ["Dataset is empty. Please supply a valid CSV file with student records."],
            "warnings": [],
            "notes": [],
        }

    # Verify marks column
    marks_col = role_mapping.get("marks")
    if not marks_col:
        errors.append("A Marks/Score column must be designated for performance analytics.")
    elif marks_col not in df.columns:
        errors.append(f"Designated Marks column '{marks_col}' was not found in the dataset.")
    else:
        # Check if numeric
        if not pd.api.types.is_numeric_dtype(df[marks_col]):
            # Try coercing to see if it's convertible
            coerced = pd.to_numeric(df[marks_col], errors="coerce")
            invalid_count = coerced.isna().sum() - df[marks_col].isna().sum()
            if invalid_count > 0:
                warnings.append(
                    f"Marks column '{marks_col}' has {invalid_count} non-numeric value(s) "
                    "that will be treated as missing if cleaned."
                )
            if coerced.dropna().empty:
                errors.append(f"Marks column '{marks_col}' contains no valid numeric data.")
        else:
            # Check range
            valid_marks = df[marks_col].dropna()
            if not valid_marks.empty:
                if (valid_marks < 0).any() or (valid_marks > 100).any():
                    min_val = valid_marks.min()
                    max_val = valid_marks.max()
                    warnings.append(
                        f"Marks range spans from {min_val:.1f} to {max_val:.1f}. "
                        "Values outside [0, 100] were detected."
                    )

    # Verify attendance column if provided
    attendance_col = role_mapping.get("attendance")
    if attendance_col:
        if attendance_col not in df.columns:
            warnings.append(f"Designated Attendance column '{attendance_col}' was not found in dataset.")
        else:
            if not pd.api.types.is_numeric_dtype(df[attendance_col]):
                warnings.append(f"Attendance column '{attendance_col}' contains non-numeric data.")
            else:
                valid_att = df[attendance_col].dropna()
                if not valid_att.empty:
                    if (valid_att < 0).any() or (valid_att > 100).any():
                        warnings.append(
                            f"Attendance values range from {valid_att.min():.1f}% to {valid_att.max():.1f}%. "
                            "Expected standard percentage range is [0%, 100%]."
                        )
    else:
        notes.append("No attendance column mapped. Attendance-based filters and correlations will be omitted.")

    # Student ID check
    student_id_col = role_mapping.get("student_id")
    if not student_id_col or student_id_col not in df.columns:
        notes.append("No unique student identifier mapped. Analytics will evaluate records row-by-row.")

    # Missing values check
    missing_count = int(df.isna().sum().sum())
    if missing_count > 0:
        warnings.append(f"The dataset contains {missing_count} missing cell(s) across its columns.")

    # Duplicate rows check
    duplicates = int(df.duplicated().sum())
    if duplicates > 0:
        warnings.append(f"The dataset contains {duplicates} exact duplicate row(s).")

    is_valid = len(errors) == 0

    return {
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "notes": notes,
    }


def clean_dataset(
    df: pd.DataFrame,
    role_mapping: Dict[str, Optional[str]],
    drop_duplicates: bool = True,
    impute_missing_numeric: bool = False,
    clip_ranges: bool = True,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Produce a non-destructive cleaned copy of the dataset.
    The original DataFrame is never modified in-place.

    Returns:
        (cleaned_df, cleaning_log)
    """
    if df is None:
        return pd.DataFrame(), ["No dataset provided to clean."]

    cleaned_df = df.copy(deep=True)
    log: List[str] = []

    # 1. Remove duplicate rows
    if drop_duplicates:
        initial_count = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates()
        dropped_dups = initial_count - len(cleaned_df)
        if dropped_dups > 0:
            log.append(f"Removed {dropped_dups} duplicate row(s).")
        else:
            log.append("No duplicate rows found.")

    # 2. Coerce numeric fields and optionally clip/impute
    marks_col = role_mapping.get("marks")
    if marks_col and marks_col in cleaned_df.columns:
        orig_na = cleaned_df[marks_col].isna().sum()
        cleaned_df[marks_col] = pd.to_numeric(cleaned_df[marks_col], errors="coerce")
        new_na = cleaned_df[marks_col].isna().sum() - orig_na
        if new_na > 0:
            log.append(f"Converted {new_na} non-numeric entry/entries in '{marks_col}' to NaN.")

        if clip_ranges:
            out_of_bounds = ((cleaned_df[marks_col] < 0) | (cleaned_df[marks_col] > 100)).sum()
            if out_of_bounds > 0:
                cleaned_df[marks_col] = cleaned_df[marks_col].clip(lower=0.0, upper=100.0)
                log.append(f"Clipped {out_of_bounds} marks value(s) into standard range [0.0, 100.0].")

        if impute_missing_numeric:
            missing_marks = cleaned_df[marks_col].isna().sum()
            if missing_marks > 0:
                mean_val = round(float(cleaned_df[marks_col].mean()), 2)
                cleaned_df[marks_col] = cleaned_df[marks_col].fillna(mean_val)
                log.append(f"Imputed {missing_marks} missing marks with column mean ({mean_val}).")

    att_col = role_mapping.get("attendance")
    if att_col and att_col in cleaned_df.columns:
        orig_na = cleaned_df[att_col].isna().sum()
        cleaned_df[att_col] = pd.to_numeric(cleaned_df[att_col], errors="coerce")
        new_na = cleaned_df[att_col].isna().sum() - orig_na
        if new_na > 0:
            log.append(f"Converted {new_na} non-numeric entry/entries in '{att_col}' to NaN.")

        if clip_ranges:
            out_of_bounds = ((cleaned_df[att_col] < 0) | (cleaned_df[att_col] > 100)).sum()
            if out_of_bounds > 0:
                cleaned_df[att_col] = cleaned_df[att_col].clip(lower=0.0, upper=100.0)
                log.append(f"Clipped {out_of_bounds} attendance value(s) into percentage range [0.0%, 100.0%].")

        if impute_missing_numeric:
            missing_att = cleaned_df[att_col].isna().sum()
            if missing_att > 0:
                mean_att = round(float(cleaned_df[att_col].mean()), 2)
                cleaned_df[att_col] = cleaned_df[att_col].fillna(mean_att)
                log.append(f"Imputed {missing_att} missing attendance values with mean ({mean_att}%).")

    return cleaned_df, log
