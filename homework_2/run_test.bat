@echo off
cd ..
call venv\Scripts\activate
pytest -vv --showlocals --strict tests\test_homework_2.py
pause