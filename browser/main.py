from PySide6.QtWidgets import QApplication
from gui_core.apply_theme import apply_theme
from browser.ui.window import BrowserWindow


def main():
    app = QApplication([])
    apply_theme(app)
    win = BrowserWindow()
    win.show()
    app.exec()


if __name__ == "__main__":
    main()