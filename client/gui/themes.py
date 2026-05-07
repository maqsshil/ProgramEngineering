# gui/themes.py
def get_theme(name):
    """
    Цветовые схемы для лабиринта:
    - Стены и проходы меняются в зависимости от темы
    - Вход/выход будут подсвечиваться отдельно (зелёный/красный)
    """
    themes = {
        'default': {'wall': '#333333', 'path': '#eeeeee', 'outline': '#aaaaaa'},
        'dark': {'wall': '#1a1a1a', 'path': '#3a3a3a', 'outline': '#555555'},
        'forest': {'wall': '#2d6a4f', 'path': '#d8f3dc', 'outline': '#95d5b2'},
        'sand': {'wall': '#b5651d', 'path': '#fefae0', 'outline': '#d4a373'}
    }
    return themes.get(name, themes['default'])