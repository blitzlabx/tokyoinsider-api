#!/usr/bin/env bash
# Blitz TokyoInsider Scraper API
# Author: Blitz (@blitzlabx)
set -euo pipefail
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --reload
