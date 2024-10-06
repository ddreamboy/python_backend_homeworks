#!/bin/bash
cd ..
source venv/bin/activate
uvicorn homework_2.web_chat.main:app --reload