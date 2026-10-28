# Sample Dataset Documentation

## Overview

The dataset in `sample_students.csv` is an **entirely synthetic and illustrative dataset** created for the demonstration, automated testing, and evaluation of **StudentPulse — Student Performance Analytics Dashboard**.

> **Important Academic & Ethical Notice:**  
> All records, student identifiers, names, marks, attendance figures, and class assignments are entirely fictitious.  
> They are strictly provided for software validation, user interface demonstration, and viva presentation.  
> They must **not** be treated as real student records or used to infer actual educational research findings.

---

## Schema Definition

| Column Name | Data Type | Description | Plausible Value Range |
| :--- | :--- | :--- | :--- |
| `student_id` | String | Unique synthetic identifier for the student | `STU101` – `STU206` |
| `student_name` | String | Fictitious student name for display | Diverse synthetic names |
| `class_section` | String | Academic cohort / section | `CS-A`, `CS-B` |
| `semester` | String | Current semester term | `Semester 3`, `Semester 4` |
| `subject` | String | Course module title | Course names (e.g., Data Structures, Operating Systems) |
| `marks` | Float | Academic marks scored (percentage/scaled 0–100) | `31.0` – `95.0` |
| `attendance_percentage` | Float | Lecture and lab attendance percentage | `51.0%` – `98.0%` |

---

## Intended Purpose

- Verify automated validation and column role detection.
- Demonstrate score distributions, subject comparisons, and attendance vs. marks analytics.
- Test configurable academic support alert thresholds without requiring real institutional data.
- Ensure cross-platform reproducibility when building and running inside Docker containers.
