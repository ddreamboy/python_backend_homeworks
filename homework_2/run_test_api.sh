#!/bin/bash
cd ..
source venv/bin/activate
pytest -vv --showlocals --strict tests/test_homework_2.py