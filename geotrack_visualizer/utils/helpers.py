import sys
import os

# Helper function to handle paths in both script and executable modes
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

# Configuration paths
CONFIG_PATH = resource_path(os.path.join('settings', 'config.json'))
SETTINGS_DIR = resource_path('settings')
