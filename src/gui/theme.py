"""Application theming utilities.

Provides dark and light themes using Qt palettes for consistent appearance
across both TimeTracking and FITS Viewer applications.
"""

from typing import Literal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor

ThemeName = Literal['dark', 'light']


def apply_light_theme(app: QApplication) -> None:
    """
    Apply light theme using standard Qt palette.
    
    Args:
        app: QApplication instance
    """
    palette = QPalette()
    
    # Window colors
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    
    # Base colors (for input fields, text areas)
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    
    # Button colors
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    
    # Selection colors
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    # Tooltip colors
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    
    # Link colors
    palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
    palette.setColor(QPalette.ColorRole.LinkVisited, QColor(128, 0, 128))
    
    # Disabled colors
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(128, 128, 128))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(128, 128, 128))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(128, 128, 128))
    
    app.setPalette(palette)
    app.setStyleSheet("")  # Clear any custom stylesheets


def apply_dark_theme(app: QApplication) -> None:
    """
    Apply dark theme using standard Qt palette.
    
    Args:
        app: QApplication instance
    """
    palette = QPalette()
    
    # Window colors
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    
    # Base colors (for input fields, text areas)
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    
    # Button colors
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    
    # Selection colors
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    # Tooltip colors
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    
    # Link colors
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.LinkVisited, QColor(148, 112, 216))
    
    # Disabled colors
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(128, 128, 128))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(128, 128, 128))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(128, 128, 128))
    
    # Additional dark theme colors
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Light, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.Midlight, QColor(62, 62, 62))
    palette.setColor(QPalette.ColorRole.Dark, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.Mid, QColor(44, 44, 44))
    palette.setColor(QPalette.ColorRole.Shadow, QColor(20, 20, 20))
    
    app.setPalette(palette)
    
    # Add stylesheet for better dark theme rendering
    app.setStyleSheet("""
        QToolTip {
            color: #ffffff;
            background-color: #353535;
            border: 1px solid #555555;
        }
        QMenu {
            background-color: #353535;
            color: #ffffff;
        }
        QMenu::item:selected {
            background-color: #2a82da;
        }
        QMenuBar {
            background-color: #353535;
            color: #ffffff;
        }
        QMenuBar::item:selected {
            background-color: #2a82da;
        }
    """)


def get_stylesheet(theme: ThemeName) -> str:
    """
    Deprecated: Returns empty string. Use apply_theme() instead.
    
    Kept for backwards compatibility.
    """
    return ""


def apply_theme(app: QApplication, theme: ThemeName) -> None:
    """Apply a theme to the given QApplication instance.

    This sets the application's palette and stylesheet using Qt's native
    theming system for consistent appearance.
    
    Args:
        app: QApplication instance
        theme: Theme name ('light' or 'dark')
    """
    if theme == 'light':
        apply_light_theme(app)
    else:
        apply_dark_theme(app)

