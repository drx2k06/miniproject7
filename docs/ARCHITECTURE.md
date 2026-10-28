# System Architecture Specification

## StudentPulse — Student Performance Analytics Dashboard

**Developer:** Daniel Richard Xavier  
**Repository:** [https://github.com/drx2k06/miniproject7.git](https://github.com/drx2k06/miniproject7.git)  
**Academic Level:** College Mini-Project / Undergraduate Laboratory Submission  

---

## 1. Architectural Overview

The **StudentPulse** system is engineered using a modular, decoupled architecture where data ingestion, validation, and statistical analysis are strictly separated from presentation logic. This enables high unit-test coverage, rapid headless execution, and containerized portability.

```
+-------------------------------------------------------------------------+
|                              Host Browser                               |
|                  http://localhost:8501 (Port 8501)                      |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                  Docker Container: studentpulse-app                     |
|                                                                         |
|  +-------------------------------------------------------------------+  |
|  |                 Streamlit Presentation Layer (app.py)             |  |
|  |                                                                   |  |
|  |  +---------------------+ +-----------------+ +-----------------+  |  |
|  |  |  Overview KPIs      | | Visualizations  | | Support Alerts  |  |  |
|  |  |  (Dynamic Metrics)  | | (Plotly Express)| | (Rule Engine)   |  |  |
|  |  +---------------------+ +-----------------+ +-----------------+  |  |
|  |  +-----------------------------------------+ +-----------------+  |  |
|  |  |  Data Explorer & Quality Audit (Tables) | | Viva Reference  |  |  |
|  |  +-----------------------------------------+ +-----------------+  |  |
|  +---------------------------------+---------------------------------+  |
|                                    |                                    |
|         +--------------------------+--------------------------+         |
|         v                                                     v         |
|  +-------------------------------+             +---------------------+  |
|  |  src/data_validation.py       |             |  src/analytics.py   |  |
|  |  - load_dataset()             |             |  - calculate_kpis() |  |
|  |  - inspect_dataframe()        |             |  - flag_support()   |  |
|  |  - detect_column_roles()      |             |  - correlation_r()  |  |
|  |  - validate_dataset()         |             |  - tier_groups()    |  |
|  |  - clean_dataset()            |             |  - filter_engine()  |  |
|  +---------------+---------------+             +----------+----------+  |
|                  |                                        |             |
|                  +--------------------+-------------------+             |
|                                       v                                 |
|                  +----------------------------------------+             |
|                  |     Data Layer (In-Memory Pandas)      |             |
|                  |  - data/sample_students.csv (Fictional)|             |
|                  |  - Uploaded institutional CSV buffer   |             |
|                  +----------------------------------------+             |
+-------------------------------------------------------------------------+
```

---

## 2. Component Breakdown

### 2.1 Presentation Layer (`app.py`)
- **Technology:** Streamlit 1.35+, Plotly 5.20+
- **Role:** Implements an interactive multi-tab graphical user interface.
- **Responsibilities:**
  - Sidebar ingestion controls (sample vs. file upload).
  - Dynamic heuristic column selector dropdowns.
  - Interactive threshold sliders (passing mark, academic review trigger, attendance warning).
  - Responsive visual chart rendering via Plotly with tooltips, box marginals, and reference guidelines.
  - Non-destructive export buttons (filtered data CSV, academic support outreach CSV, cleaned dataset copy).

### 2.2 Data Validation Layer (`src/data_validation.py`)
- **Technology:** Pandas, NumPy
- **Role:** Handles safe file parsing and schema validation without mutating original data.
- **Functions:**
  - `load_dataset()`: Implements fallback decoding (`utf-8`, `utf-8-sig`, `latin1`).
  - `inspect_dataframe()`: Calculates cell counts, column types, missingness, and duplicate rows.
  - `detect_column_roles()`: Uses regex and substring pattern matching to auto-identify column candidates for marks, attendance, subject, student ID, and semester.
  - `validate_dataset()`: Emits structured error and warning logs.
  - `clean_dataset()`: Generates an isolated sanitized copy (clipping marks/attendance to [0, 100], deduplication, numeric coercion).

### 2.3 Analytics Engine (`src/analytics.py`)
- **Technology:** Pandas, NumPy, Scipy/Pearson mechanics
- **Role:** Provides dynamic numerical computations and transparent heuristic rule evaluations.
- **Functions:**
  - `calculate_overview_metrics()`: Computes total students, overall average, average attendance, pass rates, and flag counts dynamically.
  - `flag_academic_support()`: Evaluates configurable condition boundaries:
    - Dual alert: Low Marks & Low Attendance.
    - Single alert: Low Marks or Low Attendance.
    - Satisfactory: On track.
  - `get_attendance_correlation()`: Derives Pearson's $r$ and pairs it with the formal statistical notice that correlation does not establish causality.
  - `get_tier_distribution()`: Aggregates marks into institutional grading tiers (Distinction, First Class, Second Class, Pass Class, Remedial).
  - `filter_dataset()`: Applies compound subset filters on subject, class, semester, marks range, and attendance range.

---

## 3. Data Flow Diagram

```
[User CSV File / Sample CSV]
             |
             v
     [load_dataset()] ---> (Encoding detection & DataFrame construction)
             |
             v
   [inspect_dataframe()] -> (Detect missing values, datatypes, duplicate rows)
             |
             v
  [detect_column_roles()] -> (Pre-fill column mapping options)
             |
             v
   [validate_dataset()] ---> (Check required marks column & numeric validity)
             |
             +---> [Pass] ---> [filter_dataset()] ---> [calculate_overview_metrics()]
             |                                    ---> [flag_academic_support()]
             |                                    ---> [Plotly Visualizations]
             v
          [Fail] ------------> Show actionable user remediation hints
```

---

## 4. Containerization Architecture

- **Base Image:** `python:3.11-slim` ensures minimal image footprint (~180MB compressed) and removes unnecessary build tools.
- **User Isolation:** Runs under an unprivileged user `appuser` (UID 1000) rather than `root`, adhering to CIS Docker Benchmarks.
- **Health Monitoring:** Docker polls `http://localhost:8501/_stcore/health` every 30 seconds using Python's native `urllib.request`.
- **Port Exposure:** Exposes port 8501 and binds Streamlit to `0.0.0.0` inside container network bridge.
