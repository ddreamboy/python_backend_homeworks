**Приложение для обработки HTTP-запросов**
=============================================

**Запуск приложения**
--------------------

### Windows

```bash
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
cd src
uvicorn asgi_app.main:app --reload
```

ИЛИ

Запустите файл `start.bat` 

### Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cd src
uvicorn asgi_app.main:app --reload
```

ИЛИ

1) Cделайте файл start.sh исполняемым командой `chmod +x start.sh`
2) Запустите его командой `./start.sh`
