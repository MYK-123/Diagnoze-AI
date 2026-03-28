@echo off
python -m uvicorn api.main:app --reload --host "0.0.0.0" --port 8889 --log-level debug
