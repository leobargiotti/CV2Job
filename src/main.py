import sys, os
from PyQt6.QtWidgets import QApplication
from dotenv import load_dotenv
from app import JobMatchingApp

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(dotenv_path="../.env")
    app = QApplication(sys.argv)
    window = JobMatchingApp()
    window.show()
    sys.exit(app.exec())
