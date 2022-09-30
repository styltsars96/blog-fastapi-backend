#!/usr/bin/env bash

cd "$(dirname "$0")"/.. || exit

alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
