# gui/themes.py
def get_theme(name):
    themes = {
        'winter': {...},
        'spring': {...},
        'summer': {...},
        'autumn': {...}
    }
    return themes.get(name, themes["summer"])