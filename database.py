import sqlite3
import requests
import time

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
        first_name TEXT,
        last_name TEXT,
        phone_numbers TEXT,
        addresses TEXT,
        relevance_score REAL
    )''')
    conn.commit()
    conn.close()
    print("Database initialized and table created.")

def save_document_to_db(document):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO documents (url, first_name, last_name, phone_numbers, addresses, relevance_score)
                      VALUES (?, ?, ?, ?, ?, ?)''', 
                   (document.url, document.first_name, document.last_name, ','.join(document.phone_numbers), ','.join(document.addresses), document.relevance_score))
    conn.commit()
    conn.close()
    print(f"Document saved to DB: {document.url}")

def fetch_documents_from_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''SELECT url, first_name, last_name, phone_numbers, addresses, relevance_score 
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