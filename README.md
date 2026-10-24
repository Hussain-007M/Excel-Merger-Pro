# Excel Merger Pro

A Windows desktop application for combining Excel and CSV files and joining related tables through a modern PySide6 interface.

[![Download Windows Beta](https://img.shields.io/badge/Download-v3.4.0%20Beta-7B2CBF?style=for-the-badge&logo=windows)](https://github.com/Hussain-007M/Excel-Merger-Pro/releases/download/v3.4.0-beta.1/ExcelMergerPro-Modern-Windows.zip)

**Latest modern Windows beta:** [v3.4.0-beta.1](https://github.com/Hussain-007M/Excel-Merger-Pro/releases/tag/v3.4.0-beta.1) | **Status:** Pre-release | **Platform:** Windows | **Python installation:** Not required for the packaged application.

The previous [v3.3.0 release](https://github.com/Hussain-007M/Excel-Merger-Pro/releases/tag/v3.3.0) remains available as an earlier version.

## Features

### Merge Files
- Combine CSV and XLSX files from a selected folder.
- Inspect columns and review suggested data types before merging.
- Export an Excel workbook with a merge summary and processed rows.
- View processing counts and open the report from the interface.

### Join Tables
- Join two CSV or XLSX tables using selected key columns.
- Choose a LEFT or INNER join.
- Display matched, unmatched and joined-row counts.
- Reject duplicate keys in the right table to prevent unintended multiplication.
- Preserve the original input files. Existing identifiers are not replaced in the normal workflow.

## Merge vs Join

**Merge Files** appends rows from input files. **Join Tables** combines related records using matching key values.

## Technologies

Python, PySide6 (Qt), pandas, openpyxl, pytest, and PyInstaller.

## Install the Windows beta

1. Download [ExcelMergerPro-Modern-Windows.zip](https://github.com/Hussain-007M/Excel-Merger-Pro/releases/download/v3.4.0-beta.1/ExcelMergerPro-Modern-Windows.zip).
2. Extract the ZIP file completely.
3. Open the extracted `ExcelMergerPro-Release` directory.
4. Run `ExcelMergerPro-Release.exe`; keep the `_internal` folder beside it.

The beta has been locally tested on Windows. Additional testing on other Windows computers is recommended before production use. Windows may warn about an unsigned application; review any security warning rather than bypassing protections blindly.

## Run from source

On Windows, in a virtual environment:

```powershell
python -m pip install -r requirements.txt
python modern_gui.py
```

Select **Merge Files** or **Join Tables** in the sidebar. Select input data and an output folder; the application writes an Excel report to the chosen output location.

## Tests

[![Python tests](https://github.com/Hussain-007M/Excel-Merger-Pro/actions/workflows/tests.yml/badge.svg)](https://github.com/Hussain-007M/Excel-Merger-Pro/actions/workflows/tests.yml)

```powershell
python -m pip install pytest
python -m pytest -q
```

The modern desktop code has 22 passing automated tests as of October 2026 (locally and in GitHub Actions). Tests cover data types, suggestions, merging, and core joining behavior. This does **not** mean all production edge cases are verified.

## Windows build

The repository includes a PyInstaller spec for a folder-based, windowed Windows build:

```powershell
python -m PyInstaller --noconfirm --workpath "$env:TEMP\ExcelMergerPro_build" --distpath ".\dist_release" ExcelMergerPro-Release.spec
```

Run `dist_release\ExcelMergerPro-Release\ExcelMergerPro-Release.exe`, keeping the accompanying `_internal` directory intact. The folder-based build was tested locally, but should also be validated on a separate Windows machine before public distribution.

## Screenshots

Screenshots currently in the repository may show the earlier interface. Updated captures of the modern release are planned.

![Main interface](screenshots/main_interface.png)

![Merge interface](screenshots/merge_interface.png)

![Join interface](screenshots/join_interface.png)

![Excel report](screenshots/excel_report.png)

## Branches and releases

- `main`: current repository code, including the modern PySide6 desktop application.
- `develop/modern-desktop`: development branch for ongoing work.
- [v3.4.0 Beta](https://github.com/Hussain-007M/Excel-Merger-Pro/releases/tag/v3.4.0-beta.1): modern Windows ZIP package (pre-release).
- [v3.3.0](https://github.com/Hussain-007M/Excel-Merger-Pro/releases/tag/v3.3.0): earlier Windows executable.
- [Releases](https://github.com/Hussain-007M/Excel-Merger-Pro/releases): downloadable builds and release notes.

**Data handling:** Source files are read for processing; output is written separately to the user-selected folder. Review joins and output columns before relying on reports for business-critical work.
