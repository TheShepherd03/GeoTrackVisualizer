from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, QPushButton, QFrame
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from ..utils.helpers import resource_path

class WelcomeScreen(QDialog):
    """
    Welcome screen that displays an introduction to the application's features
    using markdown formatting for a professional appearance.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to GeoTrack Visualizer")
        self.setWindowIcon(QIcon(resource_path('icons/app_icon.png')))
        self.resize(800, 600)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        # Create markdown browser with custom styling
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setStyleSheet("""
            QTextBrowser {
                border: none;
                background-color: #f8f9fa;
                padding: 20px;
                font-size: 14px;
            }
        """)
        # Load HTML content directly
        try:
            self.text_browser.setSearchPaths([resource_path('')])
            html_path = resource_path('welcome.html')
            with open(html_path, 'r') as f:
                html_content = f.read()
                self.text_browser.setHtml(html_content)
        except Exception as e:
            self.text_browser.setPlainText(f"Error loading welcome content: {e}")
        # Create a styled start button
        button_container = QFrame()
        button_layout = QHBoxLayout(button_container)
        self.start_button = QPushButton("Start Application")
        self.start_button.setMinimumSize(QSize(200, 50))
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.start_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        button_layout.addStretch()
        layout.addWidget(self.text_browser)
        layout.addWidget(button_container)
    def update_theme(self, dark_mode):
        """Update the welcome screen appearance based on dark/light mode"""
        if dark_mode:
            self.text_browser.setStyleSheet("""
                QTextBrowser {
                    border: none;
                    background-color: #2d2d2d;
                    color: #ffffff;
                    padding: 20px;
                    font-size: 14px;
                }
            """)
        else:
            self.text_browser.setStyleSheet("""
                QTextBrowser {
                    border: none;
                    background-color: #f8f9fa;
                    color: #000000;
                    padding: 20px;
                    font-size: 14px;
                }
            """)
