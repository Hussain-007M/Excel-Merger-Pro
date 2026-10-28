# Tabrion

**Merge files. Join tables. Simplify data preparation.**

Tabrion is a free Windows desktop application built with Python and PySide6. It helps you combine Excel and CSV files, connect related tables, and review data types through a straightforward interface, without needing to write code.

[![Python tests](https://github.com/Hussain-007M/Tabrion/actions/workflows/tests.yml/badge.svg)](https://github.com/Hussain-007M/Tabrion/actions/workflows/tests.yml)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-5A52C8)
![Version](https://img.shields.io/badge/Version-3.4.1-8957E5)
![License](https://img.shields.io/badge/Access-Free-2DA44E)

> **Microsoft Store status:** Tabrion 3.4.1.0 was submitted for certification on October 28, 2026. It is **not yet approved or published** in the Store. The MSIX artifact produced by GitHub Actions is unsigned and intended for Partner Center submission, not direct installation.

## What Tabrion does

### Merge Files
- Combine multiple `.xlsx` and `.csv` files from a selected folder into one Excel workbook.
- Inspect columns and review suggested data types before processing.
- See file, row, and exclusion counts in the interface.
- Export the result and open the generated report.

### Join Tables
- Connect two Excel or CSV tables by matching selected key columns.
- Choose **Left Join** or **Inner Join**.
- Review matched, unmatched, and resulting row counts.
- Detect duplicate keys in the right table to reduce unintended row multiplication.
- Preserve original input files; results are written separately.

**Merge** appends rows from multiple files. **Join** combines related records using shared keys.

## Built with

- **Python**, **PySide6 (Qt)** for the Windows desktop interface
- **pandas** and **openpyxl** for spreadsheet processing
- **pytest** for automated tests
- **PyInstaller** and **MSIX** packaging through GitHub Actions

## Run from source

Use Python in a virtual environment on Windows:

```powershell
python -m pip install -r requirements.txt
python modern_gui.py
```

Choose **Merge Files** or **Join Tables** from the sidebar, select the input data, and specify an output location.

## Quality checks

Run the automated tests:

```powershell
python -m pip install pytest
python -m pytest -q test_data_types.py test_type_suggestions.py test_merge_integration.py test_join_engine.py
```

The project has **22 passing automated tests** as of October 2026, including checks for data types, suggestions, merging, and joining. Automated tests do not guarantee that every real-world dataset or edge case is covered.

## Windows builds and releases

### Current Tabrion version: 3.4.1.0

The Microsoft Store MSIX build is produced by the [Microsoft Store packaging workflow](https://github.com/Hussain-007M/Tabrion/actions/workflows/msix-store.yml). The unsigned MSIX is for Partner Center submission; do not treat it as a signed, public installer.

### Earlier downloadable beta (legacy branding)

The [v3.4.0-beta.1 release](https://github.com/Hussain-007M/Tabrion/releases/tag/v3.4.0-beta.1) is an **older pre-release** distributed under the former name **Excel Merger Pro**. It is not the current Tabrion 3.4.1 build.

[Download the older Windows beta ZIP](https://github.com/Hussain-007M/Tabrion/releases/download/v3.4.0-beta.1/ExcelMergerPro-Modern-Windows.zip).

For that older ZIP only:
1. Extract the archive completely.
2. Open the `ExcelMergerPro-Release` folder.
3. Run `ExcelMergerPro-Release.exe`, keeping the `_internal` folder alongside it.

The [v3.3.0 release](https://github.com/Hussain-007M/Tabrion/releases/tag/v3.3.0) is also preserved for historical reference. Windows may warn about unsigned older builds; do not bypass system protections without verifying a file's origin.

## Screenshots

New Tabrion screenshots are being prepared for the repository. Images currently stored under [`screenshots/`](screenshots/) may show an earlier interface or branding; they are not representations of the latest Store submission.

## Data handling

Tabrion runs locally. It reads source spreadsheets from your computer and creates output reports in your selected location rather than uploading source files to a cloud service. Review your join keys and resulting columns before using exports for business-critical decisions.

## Project notes

- The repository retains its historical URL, `Hussain-007M/Tabrion`, to preserve existing links.
- The user-facing product name is **Tabrion**.
- Core code and historical releases are kept separate from Store certification packaging.

**Developer:** [Hussain-007M](https://github.com/Hussain-007M)
