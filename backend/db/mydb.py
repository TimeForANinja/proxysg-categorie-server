import sqlite3

class MyDB:
    def __init__(self, filename):
        self.filename = filename
        self.conn = sqlite3.connect(filename)
