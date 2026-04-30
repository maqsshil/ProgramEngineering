# db/database.py
import sqlite3
import json
import os
from config import DB_CONFIG

class DatabaseManager:
    def __init__(self):
        self.db_path = DB_CONFIG['dbname']
        self.conn = None
        self.cursor = None
        self.connect()
        self.init_tables()
        self.create_test_users()  # создаём тестовых пользователей
    
    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"Connected to SQLite database: {self.db_path}")
        except Exception as e:
            print(f"DB connection error: {e}")
            raise
    
    def init_tables(self):
        """Создаёт таблицы, если их нет"""
        # Таблица пользователей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('admin', 'player'))
            )
        ''')
        
        # Таблица лабиринтов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS mazes (
                maze_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                creation_date TEXT NOT NULL,
                height INTEGER NOT NULL,
                width INTEGER NOT NULL,
                maze_map TEXT NOT NULL,
                entry_x INTEGER NOT NULL,
                entry_y INTEGER NOT NULL,
                exit_x INTEGER NOT NULL,
                exit_y INTEGER NOT NULL
            )
        ''')
        self.conn.commit()
    
    def create_test_users(self):
        """Создаёт тестового администратора и игрока, если их нет"""
        # Проверяем, есть ли админ
        self.cursor.execute("SELECT 1 FROM users WHERE login = 'admin'")
        if not self.cursor.fetchone():
            self.create_user('admin', 'admin', 'admin')
            print("Создан тестовый администратор: admin/admin")
        
        self.cursor.execute("SELECT 1 FROM users WHERE login = 'player'")
        if not self.cursor.fetchone():
            self.create_user('player', 'player', 'player')
            print("Создан тестовый игрок: player/player")
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    # ---------- Users ----------
    def create_user(self, login, password, role):
        query = "INSERT INTO users (login, password, role) VALUES (?, ?, ?)"
        self.cursor.execute(query, (login, password, role))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_user(self, login, password):
        query = "SELECT user_id, login, role FROM users WHERE login = ? AND password = ?"
        self.cursor.execute(query, (login, password))
        row = self.cursor.fetchone()
        if row:
            return row
        return None
    
    def user_exists(self, login):
        self.cursor.execute("SELECT 1 FROM users WHERE login = ?", (login,))
        return self.cursor.fetchone() is not None
    
    # ---------- Mazes ----------
    def save_maze(self, name, height, width, maze_map, entry, exit_):
        import datetime
        creation_date = datetime.datetime.now().strftime("%Y-%m-%d")
        map_str = json.dumps(maze_map)
        query = '''
            INSERT INTO mazes (name, creation_date, height, width, maze_map, entry_x, entry_y, exit_x, exit_y)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(query, (name, creation_date, height, width, map_str, entry[0], entry[1], exit_[0], exit_[1]))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def load_all_mazes(self):
        query = "SELECT maze_id, name, creation_date, height, width, maze_map, entry_x, entry_y, exit_x, exit_y FROM mazes"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        mazes = []
        for row in rows:
            maze = {
                'id': row[0],
                'name': row[1],
                'date': row[2],
                'height': row[3],
                'width': row[4],
                'map': json.loads(row[5]),
                'entry': (row[6], row[7]),
                'exit': (row[8], row[9])
            }
            mazes.append(maze)
        return mazes
    
    def delete_maze(self, maze_id):
        self.cursor.execute("DELETE FROM mazes WHERE maze_id = ?", (maze_id,))
        self.conn.commit()