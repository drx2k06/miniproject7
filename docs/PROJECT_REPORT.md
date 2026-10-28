# Academic Project Report

# StudentPulse: A Dockerized Interactive Student Performance Analytics and Early Support Dashboard

---

**A Mini-Project Report Submitted in Partial Fulfillment of the Requirements for the Degree of Bachelor of Engineering / Technology in Computer Science and Engineering**

**Developer & Author:**  
**Daniel Richard Xavier**  
GitHub: [https://github.com/drx2k06/miniproject7.git](https://github.com/drx2k06/miniproject7.git)  
Academic Year: 2026–2027  

---

## Abstract

Academic institutions face persistent operational challenges in tracking heterogeneous student performance across courses, evaluating attendance correlation, and proactively identifying learners requiring early pedagogical intervention. Traditional approaches rely predominantly on static spreadsheets or monolithic institutional ERPs that lack responsive data visualization, require complex manual calculations, and suffer from inconsistent local execution environments ("works on my machine" syndrome).

This project presents **StudentPulse**, a lightweight, responsive, and containerized academic analytics dashboard engineered using **Python**, **Streamlit**, **Pandas**, and **Plotly**, packaged via **Docker** and **Docker Compose**. StudentPulse provides dynamic cohort KPI computation, automated schema role detection, interactive multi-dimensional filtering, non-destructive data cleaning, and transparent, rule-based academic support flags without relying on black-box predictive modeling. The application is verified through a 23-test automated Pytest suite and demonstrates high reproducibility across diverse computing platforms through containerization.

---

## 1. Introduction

In modern tertiary education, data-informed pedagogy is essential for student success and retention. Faculty and department coordinators collect substantial academic data, including internal assessment marks, laboratory examinations, and periodic attendance figures. However, raw tabular records often obscure underlying patterns, such as subject difficulty variations, bimodal score distributions, or attendance thresholds below which student comprehension diminishes.

To bridge the gap between complex enterprise business intelligence suites and inflexible spreadsheets, **StudentPulse** was engineered as an intuitive, CPU-friendly web application capable of immediate local deployment or single-command containerized execution.

---

## 2. Problem Statement

Existing academic assessment workflows suffer from several technical and operational bottlenecks:
1. **Manual Spreadsheet Dependency:** Calculating passing rates, cohort averages, and identifying students below regulatory thresholds requires manual formulas that are error-prone and non-interactive.
2. **Environment Inconsistency:** Analytical scripts developed in Python frequently encounter runtime errors when transferred between machines due to divergent dependency versions and OS-level library differences.
3. **Data Loss During Cleaning:** Standard spreadsheet tools frequently mutate original records in-place when removing duplicates or correcting formatting, destroying raw audit trails.
4. **Opaque Algorithmic Claims:** Many emerging "predictive analytics" tools employ unverified machine learning models that make speculative claims regarding student failure, risking unfair bias and ethical concerns.

---

## 3. Project Objectives

The primary objectives of the StudentPulse system include:
1. **Interactive Visualization:** Provide dynamic, responsive Plotly charts (histograms, subject bar comparisons, attendance vs. marks scatter plots, and performance tiers).
2. **Automated Schema Ingestion:** Allow users to upload arbitrary institutional CSV files with heuristic auto-mapping of academic roles (student ID, marks, attendance, subject, semester, class).
3. **Transparent Heuristic Support Indicators:** Implement clear, instructor-configurable rules for flagging students needing mentorship, avoiding black-box predictions.
4. **Non-Destructive Processing:** Ensure that raw institutional records are preserved intact while providing downloadable cleaned and filtered copies.
5. **Full Containerization:** Deliver a production-ready `Dockerfile` and `compose.yaml` with non-root security privileges and health checks to ensure zero-configuration deployment.
6. **Thorough Verification:** Establish an automated unit-test suite with 100% test pass rates covering validation, analytics, edge cases, and extreme threshold boundaries.

---

## 4. System Requirements

### 4.1 Functional Requirements
- **FR1: Dataset Ingestion & Fallback:** Support CSV uploads with multi-encoding decoding (UTF-8, Latin-1) and provide a bundled synthetic sample dataset for offline exploration.
- **FR2: Dynamic Metric Derivation:** Automatically calculate total unique students, mean marks, median marks, average attendance, and pass rate based on active filter states.
- **FR3: Interactive Multi-Dimensional Filtering:** Enable real-time filtering by subject, semester, class section, marks range, and attendance percentage.
- **FR4: Transparent Support Rule Engine:** Flag student records breaching instructor-defined score or attendance thresholds with clear reasoning explanations.
- **FR5: Data Quality Reporting & Cleaning:** Audit missing cells and duplicate rows, offering an optional downloadable sanitized dataset with logged transformations.

### 4.2 Non-Functional Requirements
- **NFR1: Portability:** Fully executable on any OS supporting Docker Desktop or Python 3.10+.
- **NFR2: Performance:** Sub-second chart rendering and filtering response times for standard institutional cohorts (<10,000 records).
- **NFR3: Security:** Execution within the container under an unprivileged user (`appuser`, UID 1000) with zero credential hardcoding.
- **NFR4: Reliability:** Automated container health monitoring via Streamlit's native `/_stcore/health` endpoint.

---

## 5. System Design and Architecture

StudentPulse follows a clean three-tier architectural paradigm:

```
+-------------------------------------------------------------+
|                      Client Browser                         |
|                   (Streamlit Web GUI)                       |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                     Application Tier                        |
|  - app.py (UI Orchestration, Layout, Session State)        |
|  - src/analytics.py (KPIs, Support Rules, Correlation)      |
|  - src/data_validation.py (Schema Detection & Sanitization) |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                        Data Tier                            |
|  - In-Memory Pandas DataFrame Storage                       |
|  - Local Synthetic CSV (data/sample_students.csv)           |
+-------------------------------------------------------------+
```

### Module Responsibilities:
- **`app.py`:** Hosts the Streamlit frontend, organizes multi-tab navigation, controls user input widgets, and dispatches data to plotting routines.
- **`src/data_validation.py`:** Isolates CSV parsing, regex-based column role detection, error handling, and non-destructive sanitization routines.
- **`src/analytics.py`:** Houses mathematical operations, pass percentage derivations, Pearson correlation calculations, and academic support flag logic.

---

## 6. Implementation Details

### 6.1 Column Role Heuristics
Rather than enforcing rigid column headers, `src/data_validation.py` scans column names using prioritized keywords and datatype checks:
- Marks: `["marks", "score", "total_marks", "grade_point", "percentage"]`
- Attendance: `["attendance_percentage", "attendance_pct", "attendance", "attendance_rate"]`
- Identifier: `["student_id", "roll_no", "usn", "reg_no", "id"]`

### 6.2 Transparent Support Indicators
The academic support mechanism avoids complex neural networks or black-box classifiers in favor of transparent pedagogical boundaries:
$$\text{Alert State} = 
\begin{cases} 
\text{Dual Risk} & \text{if } M < T_{\text{score}} \land A < T_{\text{att}} \\ 
\text{Low Marks} & \text{if } M < T_{\text{score}} \land A \ge T_{\text{att}} \\ 
\text{Low Attendance} & \text{if } M \ge T_{\text{score}} \land A < T_{\text{att}} \\ 
\text{Satisfactory} & \text{otherwise} 
\end{cases}$$
Where $M$ is student score, $A$ is attendance percentage, $T_{\text{score}}$ is the configured score threshold, and $T_{\text{att}}$ is the configured attendance threshold.

### 6.3 Ethical Correlation Notice
To uphold academic integrity and responsible data science, the attendance vs. marks scatter visualization explicitly displays the pedagogical disclaimer:
*"Correlation between attendance and marks reflects co-variation in the dataset and does NOT imply direct mathematical causation."*

---

## 7. Docker Containerization Strategy

The application is packaged into a self-contained container using `python:3.11-slim`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN useradd -m -u 1000 appuser
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./
COPY src/ ./src/
COPY data/ ./data/
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

### Key Technical Decisions:
1. **Minimal Base Image:** `python:3.11-slim` avoids multi-gigabyte OS layers.
2. **Layer Caching:** `requirements.txt` is copied and installed prior to source code copying, avoiding dependency reinstalls during UI edits.
3. **Pure-Python Health Check:** Relies on standard library `urllib.request` rather than external packages (`curl` or `wget`), preventing extraneous dependencies.

---

## 8. Verification and Results

The testing framework includes 23 unit tests across data validation and analytics modules:
- **Loading Tests:** File paths, in-memory buffers, empty CSVs, and malformed inputs.
- **Boundary Tests:** Passing rate extremes ($0\%$ vs $100\%$), out-of-range marks ($[-10, 150]$), and missing attendance.
- **Rule Tests:** Four-quadrant support trigger boundaries.
- **End-to-End Tests:** Synthetic dataset loading, role detection, and KPI calculations.
- **Smoke Test:** Local Streamlit headless startup verified with HTTP 200 response on `/_stcore/health`.

**Result:** 23 out of 23 automated tests passed successfully with 0 failures and 0 warnings.

---

## 9. Conclusion & Future Scope

### 9.1 Conclusion
StudentPulse successfully delivers an interactive, ethical, and easily explainable student performance analytics system. By decoupling the analytical logic from the web interface, the system achieves complete testability. Containerization via Docker guarantees immediate deployment on any workstation without environment configuration overhead, fulfilling all requirements for a professional academic mini-project.

### 9.2 Future Scope
1. **Multi-Semester Longitudinal Tracking:** Adding student trajectory tracking across multiple consecutive semesters to observe semester-over-semester progress.
2. **Automated PDF Grade Sheet Generation:** Exporting personalized academic performance reports for parent-teacher meetings.
3. **LMS Integration:** Connecting via secure OAuth2 APIs to platforms like Moodle or Canvas to synchronize marks directly.
4. **Role-Based Access Control (RBAC):** Supporting differentiated views for department heads, class advisors, and individual students.

---

## 10. References

1. Streamlit Documentation: *Streamlit Architecture and Execution Model*, 2026.
2. McKinney, W., *Data Analysis with Open Source Tools*, O'Reilly Media.
3. Plotly Technologies Inc., *Interactive Graphing Open Source Library*, 2026.
4. Docker Documentation: *Best Practices for Writing Dockerfiles*, Docker Inc., 2026.
5. National Education Policy (NEP) Guidelines on Continuous Academic Assessment and Mentoring.
