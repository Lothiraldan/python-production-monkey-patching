import sqlite3


def query(query):
    connection = sqlite3.connect('db.sqlite')
    cursor = connection.cursor()
    cursor.execute(query)
    return cursor.fetchone()
