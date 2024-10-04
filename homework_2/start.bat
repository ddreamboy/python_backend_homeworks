@echo off
call venv\Scripts\activate
uvicorn shop_api.main:app --reload