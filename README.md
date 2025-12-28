# Задание по вариантам к sprint7
Вариант 2: Музейный комплекс

Использовался python3.10

## Клонирование
git clone https://github.com/Andrew-Aleynik/sprint7_project.git

cd sprint7_project

## Создание и активация venv
python3 -m venv .venv
### Linux
source .venv/bin/activate
### Windows
.venv\Scripts\activate

## Обновление pip до последней версии
pip install --upgrade pip

## Установка всех зависимостей
pip install -r requirements.txt

cd museum_complex

## Создание миграций
python manage.py makemigrations

## Применение миграций
python manage.py migrate

## Загрузка начальных данных из фикстур
python manage.py loaddata db.json

## Создание суперпользователя
python manage.py createsuperuser
