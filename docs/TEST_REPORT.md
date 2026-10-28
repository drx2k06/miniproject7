# Automated Verification & Test Report

## StudentPulse — Student Performance Analytics Dashboard

**Developer:** Daniel Richard Xavier  
**Date of Testing:** October 28, 2026  
**Test Framework:** Pytest 8.3.4 (Python 3.12.10)  
**Execution Status:** **23 / 23 Tests Passed (100% Success Rate)**  

---

## 1. Test Environment Specification

- **Operating System:** Windows 11 (64-bit)
- **Python Version:** 3.12.10
- **Test Runner:** Pytest 8.3.4
- **Core Dependencies:** Pandas 3.0.6, NumPy 2.5.3, Streamlit 1.66.1, Plotly 7.1.0

---

## 2. Test Execution Summary

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-8.3.4, pluggy-1.6.0
rootdir: C:\Users\drx20\Projects\miniproject7
collected 23 items

tests/test_analytics.py::test_categorize_performance PASSED              [  4%]
tests/test_analytics.py::test_calculate_overview_metrics PASSED          [  8%]
tests/test_analytics.py::test_calculate_overview_metrics_pass_rate_extremes PASSED [ 13%]
tests/test_analytics.py::test_calculate_overview_metrics_empty PASSED    [ 17%]
tests/test_analytics.py::test_flag_academic_support_boundaries PASSED    [ 21%]
tests/test_analytics.py::test_flag_academic_support_without_attendance PASSED [ 26%]
tests/test_analytics.py::test_get_subject_statistics PASSED              [ 30%]
tests/test_analytics.py::test_get_attendance_correlation PASSED          [ 34%]
tests/test_analytics.py::test_get_tier_distribution PASSED               [ 39%]
tests/test_analytics.py::test_filter_dataset PASSED                      [ 43%]
tests/test_analytics.py::test_sample_dataset_end_to_end PASSED           [ 47%]
tests/test_data_validation.py::test_load_dataset_valid_file PASSED       [ 52%]
tests/test_data_validation.py::test_load_dataset_from_buffer PASSED      [ 56%]
tests/test_data_validation.py::test_load_dataset_empty_csv PASSED        [ 60%]
tests/test_data_validation.py::test_load_dataset_none PASSED             [ 65%]
tests/test_data_validation.py::test_inspect_dataframe PASSED             [ 69%]
tests/test_data_validation.py::test_detect_column_roles PASSED           [ 73%]
tests/test_data_validation.py::test_validate_dataset_all_valid PASSED    [ 78%]
tests/test_data_validation.py::test_validate_dataset_missing_marks_column PASSED [ 82%]
tests/test_data_validation.py::test_validate_dataset_non_numeric_marks PASSED [ 86%]
tests/test_data_validation.py::test_validate_dataset_with_warnings PASSED [ 91%]
tests/test_data_validation.py::test_clean_dataset_removes_duplicates PASSED [ 95%]
tests/test_data_validation.py::test_clean_dataset_clips_out_of_bounds_values PASSED [100%]

============================= 23 passed in 1.00s ==============================
```

---

## 3. Detailed Test Matrix

| Test ID | Module | Function Under Test | Objective / Scenario | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **TC01** | `test_data_validation` | `test_load_dataset_valid_file` | Verify loading from valid CSV file path on disk | **PASS** |
| **TC02** | `test_data_validation` | `test_load_dataset_from_buffer` | Verify loading from in-memory StringIO buffer | **PASS** |
| **TC03** | `test_data_validation` | `test_load_dataset_empty_csv` | Verify defensive error handling for zero-byte CSV | **PASS** |
| **TC04** | `test_data_validation` | `test_load_dataset_none` | Verify handling when data source is `None` | **PASS** |
| **TC05** | `test_data_validation` | `test_inspect_dataframe` | Verify row count, column detection, and missing counts | **PASS** |
| **TC06** | `test_data_validation` | `test_detect_column_roles` | Verify regex heuristic auto-mapping of academic roles | **PASS** |
| **TC07** | `test_data_validation` | `test_validate_dataset_all_valid` | Verify clean validation report on valid schema | **PASS** |
| **TC08** | `test_data_validation` | `test_validate_dataset_missing_marks_column` | Verify blocking error when marks column is missing | **PASS** |
| **TC09** | `test_data_validation` | `test_validate_dataset_non_numeric_marks` | Verify rejection when marks contain non-numeric data | **PASS** |
| **TC10** | `test_data_validation` | `test_validate_dataset_with_warnings` | Verify non-blocking warnings for out-of-range values | **PASS** |
| **TC11** | `test_data_validation` | `test_clean_dataset_removes_duplicates` | Verify non-destructive deduplication | **PASS** |
| **TC12** | `test_data_validation` | `test_clean_dataset_clips_out_of_bounds_values` | Verify bounds clipping to [0.0, 100.0] range | **PASS** |
| **TC13** | `test_analytics` | `test_categorize_performance` | Verify academic grading tiers (Distinction down to Remedial) | **PASS** |
| **TC14** | `test_analytics` | `test_calculate_overview_metrics` | Verify arithmetic accuracy of average, median, pass rate | **PASS** |
| **TC15** | `test_analytics` | `test_calculate_overview_metrics_pass_rate_extremes`| Verify boundary conditions (0% and 100% passing threshold) | **PASS** |
| **TC16** | `test_analytics` | `test_calculate_overview_metrics_empty` | Verify graceful fallback on empty DataFrame | **PASS** |
| **TC17** | `test_analytics` | `test_flag_academic_support_boundaries` | Verify four quadrant logic for support flags | **PASS** |
| **TC18** | `test_analytics` | `test_flag_academic_support_without_attendance` | Verify single-variable support rule when attendance absent | **PASS** |
| **TC19** | `test_analytics` | `test_get_subject_statistics` | Verify grouped aggregation (mean, min, max, count) per subject| **PASS** |
| **TC20** | `test_analytics` | `test_get_attendance_correlation` | Verify Pearson correlation coefficient computation | **PASS** |
| **TC21** | `test_analytics` | `test_get_tier_distribution` | Verify cohort breakdown counts across performance tiers | **PASS** |
| **TC22** | `test_analytics` | `test_filter_dataset` | Verify multi-variable compound filtering | **PASS** |
| **TC23** | `test_analytics` | `test_sample_dataset_end_to_end` | Verify bundled synthetic dataset passes full pipeline | **PASS** |

---

## 4. Streamlit Startup Smoke Test

- **Execution Command:**
  ```powershell
  python -m streamlit run app.py --server.headless=true --server.port=8501
  ```
- **Health Verification:**
  Queried `http://localhost:8501/_stcore/health` via HTTP GET.
- **HTTP Response Code:** `200 OK`
- **Response Body:** `ok`
- **Result:** **PASSED**. Application starts headlessly, initializes session state, renders widgets, and responds to health monitoring without runtime exceptions.
