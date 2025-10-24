# interface.py
import logging
import sys
import os

# Add the parent directory to Python path so we can import from Logic and Graphic
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from Graphic.interface import NewsApp

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('news_app.log'),  # Log to file
            logging.StreamHandler(sys.stdout)     # Log to console
        ]
    )

if __name__ == "__main__":
    setup_logging()
    app = QApplication(sys.argv)
    window = NewsApp()
    window.show()
    sys.exit(app.exec())