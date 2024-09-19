python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
cd src
uvicorn asgi_app.main:app --reload
