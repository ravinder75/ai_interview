#!/bin/bash
set -e

cd /opt/render/project/src/backend || cd "$(dirname "$0")"
pip install --upgrade pip
pip install -r requirements.txt

exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8005}
