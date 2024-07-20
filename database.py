import sqlite3
import requests
import time
import os

"""

"""
# Database setup
DATABASE = 'web_crawler.sqlite'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        info TEXT,
        relevance_score TEXT,
        name_relevance_score TEXT,
        birthday_relevance_score TEXT,
        phone_relevance_score TEXT,  
        address_relevance_score TEXT,
        zipcode_relevance_score TEXT,
        picture_relevance_score TEXT       
    )''')
    conn.commit()
    conn.close()
    print("Database initialized and table created.")

def save_document_to_db(document):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO documents (url, info, relevance_score, name_relevance_score, birthday_relevance_score, phone_relevance_score, address_relevance_score, zipcode_relevance_score, picture_relevance_score)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                   (document.url, document.info, document.relevance_score, document.name_relevance_score, document.birthday_relevance_score, document.phone_relevance_score, document.address_relevance_score, document.zipcode_relevance_score, document.picture_relevance_score))
    conn.commit()
    conn.close()
    print(f"Document saved to DB: {document.url}")

def fetch_documents_from_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''SELECT url, info, relevance_score, name_relevance_score, birthday_relevance_score, phone_relevance_score, address_relevance_score, zipcode_relevance_score, picture_relevance_score
                      FROM documents
                      ORDER BY relevance_score DESC''')
    rows = cursor.fetchall()
    conn.close()
    return rows

def clear_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents")
    conn.commit()
    conn.close()

def get_db_mtime():
    return os.path.getmtime(DATABASE)