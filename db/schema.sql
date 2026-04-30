-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    login VARCHAR(10) NOT NULL UNIQUE,
    password VARCHAR(10) NOT NULL,  -- В реальном проекте хранить хеш, здесь – для учебных целей
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'player'))
);

-- Таблица лабиринтов
CREATE TABLE IF NOT EXISTS mazes (
    maze_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    creation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    height INTEGER NOT NULL CHECK (height >= 5 AND height <= 25 AND height % 2 = 1),
    width INTEGER NOT NULL CHECK (width >= 5 AND width <= 25 AND width % 2 = 1),
    maze_map TEXT NOT NULL,        -- сериализованная матрица, например, в JSON или построчно
    entry_x INTEGER NOT NULL,
    entry_y INTEGER NOT NULL,
    exit_x INTEGER NOT NULL,
    exit_y INTEGER NOT NULL
);