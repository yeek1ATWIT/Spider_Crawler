from ui import WebCrawlerApp
from PyQt5.QtWidgets import QApplication
import sys
from database import init_db, clear_database

"""
TODO
Run this one. This File.
"""
def main():
    init_db()
    clear_database()
    app = QApplication(sys.argv)
    ex = WebCrawlerApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
