import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    conn = sqlite3.connect('db/audio_dictionary.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS words
                 (id INTEGER PRIMARY KEY, word TEXT NOT NULL, meaning TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS favorites
                 (user_id INTEGER, word_id INTEGER, 
                  FOREIGN KEY(user_id) REFERENCES users(id), 
                  FOREIGN KEY(word_id) REFERENCES words(id),
                  PRIMARY KEY(user_id, word_id))''')
    conn.commit()
    conn.close()

def add_word_to_database(word, meaning):
    conn = sqlite3.connect('db/audio_dictionary.db')
    c = conn.cursor()
    c.execute("INSERT INTO words (word, meaning) VALUES (?, ?)", (word, meaning))
    conn.commit()
    conn.close()

def get_word_id(word):
    conn = sqlite3.connect('db/audio_dictionary.db')
    c = conn.cursor()
    c.execute("SELECT id FROM words WHERE word=?", (word,))
    word_id = c.fetchone()
    conn.close()
    return word_id[0] if word_id else None

def add_favorite(user_id, word_id):
    conn = sqlite3.connect('db/audio_dictionary.db')
    c = conn.cursor()
    c.execute("INSERT INTO favorites (user_id, word_id) VALUES (?, ?)", (user_id, word_id))
    conn.commit()
    conn.close()

def get_favorites(user_id):
    conn = sqlite3.connect('db/audio_dictionary.db')
    c = conn.cursor()
    c.execute('''SELECT words.word, words.meaning 
                 FROM words 
                 JOIN favorites ON words.id = favorites.word_id 
                 WHERE favorites.user_id=?''', (user_id,))
    favorites = c.fetchall()
    conn.close()
    return favorites

def create_user(username, password):
    hashed_password = generate_password_hash(password)  # Default method is 'pbkdf2:sha256'
    conn = sqlite3.connect('db/audio_dictionary.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect('db/audio_dictionary.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = sqlite3.connect('db/audio_dictionary.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user_data = c.fetchone()
    conn.close()
    return user_data

def is_favorite(user_id, word_id):
    conn = sqlite3.connect('db/audio_dictionary.db')
    c = conn.cursor()
    c.execute("SELECT 1 FROM favorites WHERE user_id=? AND word_id=?", (user_id, word_id))
    result = c.fetchone()
    conn.close()
    return result is not None

def remove_favorite(user_id, word_id):
    conn = sqlite3.connect('db/audio_dictionary.db')
    c = conn.cursor()
    c.execute("DELETE FROM favorites WHERE user_id=? AND word_id=?", (user_id, word_id))
    conn.commit()
    conn.close()

def check_password(stored_password, provided_password):
    return check_password_hash(stored_password, provided_password)