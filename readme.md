Чтобы запустить ПО, нужно:

1. Установить зависимости. 
pip install -r requirements.txt

2. Установить PostgreSQL и создать базу данных
CREATE DATABASE maze_db;

3. Настроить подключение к бд
в файле server/config.py указать свой пароль:
DB_CONFIG = {
    "host": "localhost",
    "database": "maze_db",
    "user": "postgres",
    "password": "ваш_пароль"
}

4. Запустить сервер
Запустить файл server/app.py

5. Запустить клиент
В ОТДЕЛЬНОМ терминале запустить client/main.py