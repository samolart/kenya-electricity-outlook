#!/usr/bin/env bash
# Rebuild everything from the raw data. Run from the repository root.
set -euo pipefail
python3 -I src/01_build_dataset.py
python3 -I src/02_forecast_models.py
python3 -I src/03_security_stress_scenarios.py
python3 -I src/04_figures.py
python3 -I src/05_build_final_report.py
python3 -I src/06_build_technical_report.py
python3 -I src/07_build_dashboard.py
# optional: PDF versions (needs LibreOffice)
if command -v soffice >/dev/null 2>&1; then (cd reports && soffice --headless --convert-to pdf *.docx >/dev/null 2>&1); fi
echo "Done. See reports/ and outputs/."
