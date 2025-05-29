import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'foodplan.db')

def get_db_connection():
    cnx = sqlite3.connect(DB_PATH)
    cnx.row_factory = sqlite3.Row
    return cnx

def init_db():
    with open(os.path.join(os.path.dirname(__file__), 'foodplan.sql')) as f:
        sql = f.read()
    cnx = get_db_connection()
    cnx.executescript(sql)
    cnx.commit()
    cnx.close()
