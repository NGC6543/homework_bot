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
python3 -m venv env
```
```
source env/bin/activate
```

## Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```

## Выполнить миграции:
```
python3 manage.py migrate
```
## Запустить проект:
```
python3 manage.py runserver
```

# Стек технологий:
- Python
- telebot
