import sqlite3
import json
import hashlib

# Connect to SQLite database
conn = sqlite3.connect("exam_system.db")
c = conn.cursor()

def create_connection():
    conn = sqlite3.connect("exam_system.db")
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    
# Create Users Table
c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        college TEXT NOT NULL,
        registration_number TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
""")

# Create Questions Table
c.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        options TEXT NOT NULL,
        correct_option INTEGER NOT NULL
    )
""")

conn.commit()

# Insert Sample Questions if not exists
questions = [
    {"question": "What is the capital of France?", "options": ["Paris", "London", "Berlin", "Madrid"], "correct_option": 0},
    {"question": "Which planet is known as the Red Planet?", "options": ["Earth", "Mars", "Jupiter", "Venus"], "correct_option": 1},
    {"question": "What is the largest mammal?", "options": ["Elephant", "Blue Whale", "Giraffe", "Dolphin"], "correct_option": 1},
    {"question": "Who wrote 'To Kill a Mockingbird'?", "options": ["Harper Lee", "J.K. Rowling", "Ernest Hemingway", "Mark Twain"], "correct_option": 0},
    {"question": "What is the currency of Japan?", "options": ["Yen", "Dollar", "Euro", "Rupee"], "correct_option": 0},
]

c.execute("SELECT COUNT(*) FROM questions")
if c.fetchone()[0] == 0:
    for q in questions:
        c.execute("INSERT INTO questions (question, options, correct_option) VALUES (?, ?, ?)",
                  (q["question"], json.dumps(q["options"]), q["correct_option"]))
    conn.commit()
    print("Sample questions added.")

print("Database setup complete.")
conn.close()
