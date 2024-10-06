**Приложение для обработки HTTP-запросов и веб-чата**
====================================================

**Запуск приложения**
--------------------

### Запуск Shop API

#### Windows

```bash
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
uvicorn homework_2.shop_api.main:app --reload
```

ИЛИ

Запустите файл `run_test_api.bat` в `homework_2/`

#### Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
uvicorn homework_2.shop_api.main:app --reload
```

ИЛИ

1. Сделайте файл `run_test_api.sh` исполняемым командой `chmod +x run_test_api.sh` в `homework_2/`
2. Запустите его командой `./run_test_api.sh`

### Запуск Web Chat

#### Windows

```bash
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
uvicorn homework_2.web_chat.main:app --reload
```

ИЛИ

Запустите файл `start_web_chat.bat` в `homework_2/`

#### Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
uvicorn homework_2.web_chat.main:app --reload
```

ИЛИ

1. Сделайте файл `start_web_chat.sh` исполняемым командой `chmod +x start_web_chat.sh` в `homework_2/`
2. Запустите его командой `./start_web_chat.sh`

**Запуск тестов**
-----------------

### Windows

Запустите файл `run_test_api.bat` в `homework_2/`

### Linux

Запустите файл `run_test_api.sh` в `homework_2/`