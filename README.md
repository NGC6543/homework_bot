# Описание

Телеграм-бот, который периодические запрашивает информацию от сервиса https://practicum.yandex.ru/api/user_api/homework_statuses/ статус домашней работы. Если статус был изменен, то присылается уведомление пользователю.
Проект реализован с помощью библиотеки telebot.

# Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```bash
git clone https://github.com/NGC6543/homework_bot.git
```

```bash
cd homework_bot
```

## Cоздать и активировать виртуальное окружение:
```
python -m venv env
```
```
source env/bin/activate
```

## Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```

## Создать файл .env и добавить туда следующие переменные:
```
PRACTICUM_TOKEN = <Токен практикума>
TELEGRAM_TOKEN = <Токен бота>
TELEGRAM_CHAT_ID = <Токен чата, куда присылать уведомления>
```
## Запустить бота:
```
python homework.py
```

# Стек технологий:
- Python
- telebot
