#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cd src
uvicorn asgi_app.main:app --reload