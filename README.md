# Социальная сеть Yatube
### Описание
Проект представляет собой социальную сеть, функционал которой позволяет создавать личные страницы, публиковать записи, подписываться на любимых авторов и отмечать понравившиеся записи.
### Используемые технологии
<li>Python 3.7</li>
<li>Django 2.2.19</li>
<li>SQLite</li>
<li>HTML/CSS</li>
<h2>Установка проекта:</h2>

### Клонируйте репозиторий:
```git clone https://github.com/Evansmia/yatube.git```
### Перейдите в папку проекта:
```cd yatube/```
### Создайте и активируйте виртуальное окружение
```
python -m venv venv
source ./venv/Scripts/activate  #для Windows
source ./venv/bin/activate      #для Linux и macOS
```
### Установите требуемые зависимости
```
pip install -r requirements.txt
```
### Примените миграции
```
python manage.py migrate
```
### Запустите django-сервер
```
python manage.py runserver
```

### Приложение будет доступно по адресу: http://127.0.0.1:8000/
