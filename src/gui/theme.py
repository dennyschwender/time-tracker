"""Application theming utilities.

Provides dark and light stylesheets and a helper to apply a named theme to a
QApplication instance. Themes are intentionally minimal — they set common
widget colors and let individual widgets inherit or override as needed.
"""

from typing import Literal

ThemeName = Literal['dark', 'light']


_DARK = """
/* Dark theme - improved contrast */
QMainWindow {
  background-color: #181818;
  color: #ffffff;
}
QWidget {
  background-color: #181818;
  color: #ffffff;
}
QLabel, QLineEdit, QTextEdit {
  color: #ffffff;
}
QPushButton {
  background-color: #262626;
  color: #ffffff;
  border: 1px solid #333333;
}
QPushButton:hover { background-color: #2e2e2e; }
QCalendarWidget QWidget { background-color: #1f1f1f; color: #ffffff; }
QListWidget { background-color: #151515; color: #ffffff; }
QListWidget::item:selected { background: #2b6ef0; color: #ffffff; }

/* dialogs */
QMessageBox { background-color: #202020; color: #ffffff; }
"""


_LIGHT = """
/* Light theme - increased contrast */
QMainWindow { background-color: #ffffff; color: #0b0f13; }
QWidget { background-color: #ffffff; color: #0b0f13; }
QLabel, QLineEdit, QTextEdit { color: #0b0f13; }
QPushButton { background-color: #f0f6ff; color: #0b0f13; border: 1px solid #cfd9e8; }
QPushButton:hover { background-color: #e6f0ff; }
QCalendarWidget QWidget { background-color: #ffffff; color: #0b0f13; }
/* header-like area for lists */
QListWidget { background-color: #ffffff; color: #0b0f13; border: 1px solid #dbe6f3; }
/* stronger selection for light theme */
QListWidget::item:selected { background: #8fc3ff; color: #04131d; }

/* dialogs */
QMessageBox { background-color: #ffffff; color: #0b0f13; }
"""


def get_stylesheet(theme: ThemeName) -> str:
    if theme == 'light':
        return _LIGHT
    return _DARK


def apply_theme(app, theme: ThemeName) -> None:
    """Apply a theme to the given QApplication-like object.

    This sets the application's stylesheet. `app` should be the running
    QApplication instance (e.g. QApplication.instance()).
    """
    app.setStyleSheet(get_stylesheet(theme))
