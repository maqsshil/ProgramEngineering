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
            login VARCHAR(10) UNIQUE NOT NULL,
            password VARCHAR(10) NOT NULL,
            role VARCHAR(6) NOT NULL
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS mazes (
            id SERIAL PRIMARY KEY,
            name VARCHAR(20) UNIQUE NOT NULL,
            height INTEGER NOT NULL,
            width INTEGER NOT NULL,
            maze_map TEXT NOT NULL,
            theme VARCHAR(6) NOT NULL,
            entry_x INTEGER NOT NULL,
            entry_y INTEGER NOT NULL,
            exit_x INTEGER NOT NULL,
            exit_y INTEGER NOT NULL
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
        self.cursor.execute("""
            SELECT id, name, height, width,
                maze_map, theme,
                entry_x, entry_y,
                exit_x, exit_y
            FROM mazes
        """)
        rows = self.cursor.fetchall()

        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "name": row[1],
                "height": row[2],
                "width": row[3],
                "map": json.loads(row[4]),
                "theme": row[5],
                "entry": (row[6], row[7]),
                "exit": (row[8], row[9])
            })

        return result
    
    def delete_maze(self, maze_id):
        self.cursor.execute("DELETE FROM mazes WHERE id=%s", (maze_id,))
        self.conn.commit()

    def save_maze(self, name, height, width, maze_map, theme, entry, exit_):
        try:
            self.cursor.execute(
                """
                INSERT INTO mazes (name, height, width, maze_map,
                theme,
                entry_x, entry_y, exit_x, exit_y)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    name,
                    height,
                    width,
                    json.dumps(maze_map),
                    theme,
                    entry[0], entry[1],
                    exit_[0], exit_[1]
                )
            )
            self.conn.commit()
            return True
        except:
            self.conn.rollback()
            return False