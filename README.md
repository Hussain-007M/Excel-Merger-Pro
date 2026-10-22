# Excel Merger Pro v3.3

[![Download for Windows](https://img.shields.io/badge/Download-Windows%20EXE-7B2CBF?style=for-the-badge&logo=windows)](https://github.com/Hussain-007M/Excel-Merger-Pro/releases/download/v3.3.0/ExcelMergerPro_v3.3.0.exe)

**Latest Release:** v3.3.0 | **Platform:** Windows | **Python Installation:** Not Required


A Python desktop application for automating Excel and CSV data processing.

Excel Merger Pro helps users combine multiple datasets, join related tables, and generate organized Excel reports through a graphical user interface.

## Features

### MERGE Files
- Combine multiple CSV and XLSX files into one dataset.
- Map, select, and reorder output columns.
- Remove completely empty rows.
- Automatically format Excel reports.
- Generate a Merge Summary with processing statistics.

### JOIN Tables
- Join two CSV or XLSX datasets using matching columns.
- Support LEFT JOIN and INNER JOIN.
- Identify matched and unmatched records.
- Generate optional readable identifiers.
- Preserve original identifiers in hidden Excel columns.
- Export results with a Join Summary.

## MERGE vs JOIN

**MERGE** stacks rows from multiple datasets into one table, similar to Append Queries in Excel Power Query.

**JOIN** connects related records from two datasets using matching keys, similar to Merge Queries in Excel Power Query.

## Technologies

- Python
- Pandas
- OpenPyXL
- Tkinter
- PyInstaller

## Installation

Requires Python 3 and a working Tkinter installation.

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
python modern_gui.py
```

## Platform

Developed and tested on Windows.

## Project Status

Version 3.3. Source code is available for portfolio and development purposes.

## Screenshots

### Main Interface
![Main Interface](screenshots/main_interface.png)

### MERGE Interface
![MERGE Interface](screenshots/merge_interface.png)

### JOIN Interface
![JOIN Interface](screenshots/join_interface.png)

### Excel Report
![Excel Report](screenshots/excel_report.png)
