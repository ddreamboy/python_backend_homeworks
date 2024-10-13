#!/bin/bash
cd ..
source venv/bin/activate
pytest -vv --strict --showlocals --cov=homework_4/demo_service --cov-report=term-missing tests/test_homework_4.py
