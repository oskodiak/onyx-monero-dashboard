"""
Onyx Arctic Terminal Theme
Professional color scheme and styling for Onyx Monero GUI
Onyx Digital Intelligence Development
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtWidgets import QApplication

class OnyxTheme:
    """Onyx Arctic Terminal color scheme and styling"""
    
    # Core Colors - Onyx Arctic Terminal
    BACKGROUND_MAIN = "#11151C"      # Near-black graphite
    BACKGROUND_PANEL = "#161B22"     # Panel/card background
    BACKGROUND_CARD = "#1B2230"      # Elevated cards
    
    # Accent Colors
    PRIMARY_ACCENT = "#3BA6FF"       # Cool slate/ice blue
    SUCCESS = "#4CAF50"              # Muted green
    WARNING = "#FFC107"              # Amber
    DANGER = "#F44336"               # Soft red
    
    # Text Colors
    TEXT_PRIMARY = "#E5E5E5"         # Light gray
    TEXT_SECONDARY = "#A0A7B4"       # Muted gray
    TEXT_DISABLED = "#6B7280"        # Dark gray
    
    # Border/Accent
    BORDER_SUBTLE = "#252B36"        # Very subtle borders
    BORDER_FOCUS = "#3BA6FF"         # Focus borders
    
    # Fonts
    FONT_FAMILY = "Arial"            # Clean sans-serif
    FONT_MONO = "Consolas"           # Monospace for logs
    
    @staticmethod
    def apply_to_app(app: QApplication):
        """Apply Onyx theme to entire application"""
        app.setStyle("Fusion")
        
        # Create dark palette
        palette = QPalette()
        
        # Window colors
        palette.setColor(QPalette.ColorRole.Window, QColor(OnyxTheme.BACKGROUND_MAIN))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(OnyxTheme.TEXT_PRIMARY))
        
        # Base colors (input backgrounds)
        palette.setColor(QPalette.ColorRole.Base, QColor(OnyxTheme.BACKGROUND_PANEL))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(OnyxTheme.BACKGROUND_CARD))
        
        # Text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(OnyxTheme.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(OnyxTheme.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(OnyxTheme.TEXT_PRIMARY))
        
        # Button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(OnyxTheme.BACKGROUND_PANEL))
        
        # Highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, QColor(OnyxTheme.PRIMARY_ACCENT))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(OnyxTheme.TEXT_PRIMARY))
        
        # Disabled colors
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(OnyxTheme.TEXT_DISABLED))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(OnyxTheme.TEXT_DISABLED))
        
        app.setPalette(palette)
    
    @staticmethod
    def get_button_style(variant: str = "primary") -> str:
        """Get button stylesheet for different variants"""
        base_style = f"""
            QPushButton {{
                font-family: {OnyxTheme.FONT_FAMILY};
                font-size: 13px;
                font-weight: 600;
                padding: 12px 24px;
                border: 2px solid transparent;
                border-radius: 6px;
                text-align: center;
            }}
            QPushButton:disabled {{
                color: {OnyxTheme.TEXT_DISABLED};
                background: {OnyxTheme.BACKGROUND_PANEL};
                border-color: {OnyxTheme.BORDER_SUBTLE};
            }}
            QPushButton:focus {{
                border-color: {OnyxTheme.BORDER_FOCUS};
                outline: none;
            }}
        """
        
        if variant == "primary":
            return base_style + f"""
                QPushButton {{
                    background: {OnyxTheme.PRIMARY_ACCENT};
                    color: white;
                }}
                QPushButton:hover {{
                    background: #2E95EA;
                }}
                QPushButton:pressed {{
                    background: #2080D0;
                }}
            """
        elif variant == "success":
            return base_style + f"""
                QPushButton {{
                    background: {OnyxTheme.SUCCESS};
                    color: white;
                }}
                QPushButton:hover {{
                    background: #45A047;
                }}
                QPushButton:pressed {{
                    background: #3D8B40;
                }}
            """
        elif variant == "danger":
            return base_style + f"""
                QPushButton {{
                    background: {OnyxTheme.DANGER};
                    color: white;
                }}
                QPushButton:hover {{
                    background: #E53935;
                }}
                QPushButton:pressed {{
                    background: #C62828;
                }}
            """
        elif variant == "secondary":
            return base_style + f"""
                QPushButton {{
                    background: {OnyxTheme.BACKGROUND_CARD};
                    color: {OnyxTheme.TEXT_PRIMARY};
                    border-color: {OnyxTheme.BORDER_SUBTLE};
                }}
                QPushButton:hover {{
                    background: #212936;
                    border-color: {OnyxTheme.PRIMARY_ACCENT};
                }}
                QPushButton:pressed {{
                    background: #1E2530;
                }}
            """
        else:
            return base_style
    
    @staticmethod
    def get_panel_style() -> str:
        """Get panel/groupbox stylesheet"""
        return f"""
            QGroupBox {{
                font-family: {OnyxTheme.FONT_FAMILY};
                font-size: 14px;
                font-weight: 600;
                color: {OnyxTheme.TEXT_PRIMARY};
                background: {OnyxTheme.BACKGROUND_PANEL};
                border: 1px solid {OnyxTheme.BORDER_SUBTLE};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: {OnyxTheme.PRIMARY_ACCENT};
                background: {OnyxTheme.BACKGROUND_PANEL};
            }}
        """
    
    @staticmethod
    def get_status_label_style(status_type: str = "normal") -> str:
        """Get status label stylesheet"""
        base_style = f"""
            QLabel {{
                font-family: {OnyxTheme.FONT_FAMILY};
                font-size: 13px;
                padding: 8px 12px;
                border-radius: 6px;
                background: {OnyxTheme.BACKGROUND_CARD};
                border: 1px solid {OnyxTheme.BORDER_SUBTLE};
            }}
        """
        
        if status_type == "active":
            return base_style + f"""
                QLabel {{
                    color: {OnyxTheme.SUCCESS};
                    border-color: {OnyxTheme.SUCCESS};
                    background: rgba(76, 175, 80, 0.1);
                }}
            """
        elif status_type == "error":
            return base_style + f"""
                QLabel {{
                    color: {OnyxTheme.DANGER};
                    border-color: {OnyxTheme.DANGER};
                    background: rgba(244, 67, 54, 0.1);
                }}
            """
        elif status_type == "warning":
            return base_style + f"""
                QLabel {{
                    color: {OnyxTheme.WARNING};
                    border-color: {OnyxTheme.WARNING};
                    background: rgba(255, 193, 7, 0.1);
                }}
            """
        else:
            return base_style + f"""
                QLabel {{
                    color: {OnyxTheme.TEXT_SECONDARY};
                }}
            """
    
    @staticmethod
    def get_log_panel_style() -> str:
        """Get log panel stylesheet"""
        return f"""
            QTextEdit {{
                font-family: {OnyxTheme.FONT_MONO};
                font-size: 11px;
                background: {OnyxTheme.BACKGROUND_MAIN};
                color: {OnyxTheme.TEXT_SECONDARY};
                border: 1px solid {OnyxTheme.BORDER_SUBTLE};
                border-radius: 6px;
                padding: 8px;
                selection-background-color: {OnyxTheme.PRIMARY_ACCENT};
            }}
            QScrollBar:vertical {{
                background: {OnyxTheme.BACKGROUND_PANEL};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {OnyxTheme.BORDER_SUBTLE};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {OnyxTheme.PRIMARY_ACCENT};
            }}
        """
    
    @staticmethod
    def get_main_window_style() -> str:
        """Get main window stylesheet"""
        return f"""
            QMainWindow {{
                background: {OnyxTheme.BACKGROUND_MAIN};
                color: {OnyxTheme.TEXT_PRIMARY};
            }}
            QWidget {{
                font-family: {OnyxTheme.FONT_FAMILY};
                background: transparent;
            }}
        """
    
    @staticmethod
    def get_input_style() -> str:
        """Get input field stylesheet"""
        return f"""
            QLineEdit {{
                font-family: {OnyxTheme.FONT_FAMILY};
                font-size: 12px;
                padding: 8px 12px;
                background: {OnyxTheme.BACKGROUND_CARD};
                color: {OnyxTheme.TEXT_PRIMARY};
                border: 1px solid {OnyxTheme.BORDER_SUBTLE};
                border-radius: 6px;
            }}
            QLineEdit:focus {{
                border-color: {OnyxTheme.PRIMARY_ACCENT};
                outline: none;
            }}
            QLineEdit:disabled {{
                color: {OnyxTheme.TEXT_DISABLED};
                background: {OnyxTheme.BACKGROUND_PANEL};
            }}
            QComboBox {{
                font-family: {OnyxTheme.FONT_FAMILY};
                font-size: 12px;
                padding: 8px 12px;
                background: {OnyxTheme.BACKGROUND_CARD};
                color: {OnyxTheme.TEXT_PRIMARY};
                border: 1px solid {OnyxTheme.BORDER_SUBTLE};
                border-radius: 6px;
            }}
            QComboBox:focus {{
                border-color: {OnyxTheme.PRIMARY_ACCENT};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {OnyxTheme.TEXT_SECONDARY};
            }}
        """
    
    @staticmethod
    def get_dialog_style() -> str:
        """Get dialog window stylesheet"""
        return f"""
            QDialog {{
                background: {OnyxTheme.BACKGROUND_MAIN};
                color: {OnyxTheme.TEXT_PRIMARY};
            }}
        """

# Font utilities
class FontManager:
    """Font management utilities"""
    
    @staticmethod
    def get_primary_font(size: int = 12, weight: int = 400) -> QFont:
        """Get primary UI font"""
        font = QFont(OnyxTheme.FONT_FAMILY, size)
        font.setWeight(weight)
        return font
    
    @staticmethod
    def get_monospace_font(size: int = 11) -> QFont:
        """Get monospace font for logs/code"""
        font = QFont(OnyxTheme.FONT_MONO, size)
        return font
    
    @staticmethod
    def get_title_font(size: int = 16) -> QFont:
        """Get title font"""
        font = QFont(OnyxTheme.FONT_FAMILY, size)
        font.setWeight(700)  # Bold
        return font