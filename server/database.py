import psycopg2
import json
from config import DB_CONFIG


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        self.cursor = self.conn.cursor()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            login VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            role VARCHAR(20) NOT NULL
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS mazes (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            height INT,
            width INT,
            maze_map TEXT
        );
        """)

        self.conn.commit()

    def create_user(self, login, password, role):
        try:
            self.cursor.execute(
                "INSERT INTO users (login, password, role) VALUES (%s, %s, %s)",
                (login, password, role)
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def get_user(self, login, password):
        try:
            self.cursor.execute(
                "SELECT id, login, role FROM users WHERE login=%s AND password=%s",
                (login, password)
            )
            return self.cursor.fetchone()
        except Exception:
            self.conn.rollback()
            return None

    def get_all_mazes(self):
        self.cursor.execute("SELECT id, name, height, width, maze_map FROM mazes")
        rows = self.cursor.fetchall()

        result = []
        for row in rows:
            maze = json.loads(row[4])

            result.append({
                "id": row[0],
                "name": row[1],
                "height": row[2],
                "width": row[3],
                "map": maze,
                "entry": None,
                "exit": None
            })

        return result
    
    def delete_maze(self, maze_id):
        self.cursor.execute("DELETE FROM mazes WHERE id=%s", (maze_id,))
        self.conn.commit()

    def save_maze(self, name, height, width, maze_map):
        self.cursor.execute(
            "INSERT INTO mazes (name, height, width, maze_map) VALUES (%s, %s, %s, %s)",
            (name, height, width, json.dumps(maze_map))
        )
        self.conn.commit()