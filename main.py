import sys
from PyQt6.QtWidgets import QApplication
from ui_main import InsuranceApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = InsuranceApp("ghardash.xlsx")
    win.show()
    sys.exit(app.exec())
