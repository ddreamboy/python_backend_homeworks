@echo off
cd ..
call venv\Scripts\activate
uvicorn homework_2.web_chat.main:app --reload
pause