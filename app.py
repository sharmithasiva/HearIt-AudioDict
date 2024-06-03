from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
from gtts import gTTS
import os
import sqlite3
import models
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'supersecretkey'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Ensures users are redirected to the login page

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    user_data = models.get_user_by_id(user_id)
    if user_data:
        return User(*user_data)
    return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        models.create_user(username, password)
        flash('User created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = models.get_user(username)
        if user and models.check_password(user[2], password):
            login_user(User(*user))
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        word = request.form['word']
        return redirect(url_for('result', word=word))
    return render_template('index.html')

@app.route('/result/<word>', methods=['GET'])
def result(word):
    meaning = get_word_meaning(word)
    word_id = models.get_word_id(word)
    is_favorite = False
    if current_user.is_authenticated:
        is_favorite = models.is_favorite(current_user.id, word_id)
    
    if meaning != "Word not found":
        word_audio_path, meaning_audio_path = generate_audio_for_word_and_meaning(word, meaning)
    else:
        word_audio_path = None
        meaning_audio_path = None
    
    return render_template('result.html', word=word, meaning=meaning, word_audio_path=word_audio_path, meaning_audio_path=meaning_audio_path, is_favorite=is_favorite)

@app.route('/add_to_favorites/<word>', methods=['POST'])
@login_required
def add_to_favorites(word):
    word_id = models.get_word_id(word)
    if not models.is_favorite(current_user.id, word_id):
        models.add_favorite(current_user.id, word_id)
        flash('Word added to favorites!', 'success')
    else:
        flash('Word is already in favorites.', 'info')
    return redirect(url_for('result', word=word))

@app.route('/favorites')
@login_required
def favorites():
    favorite_words = models.get_favorites(current_user.id)
    return render_template('favorites.html', favorites=favorite_words)

@app.route('/remove_favorite/<word>', methods=['DELETE'])
@login_required
def remove_favorite(word):
    print('Removing favorite for word:', word)  # Add this print statement
    word_id = models.get_word_id(word)
    if models.is_favorite(current_user.id, word_id):
        models.remove_favorite(current_user.id, word_id)
        print('Favorite removed')  # Add this print statement
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error'})


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
# Utility functions

def get_word_meaning(word):
    conn = sqlite3.connect('db/audio_dictionary.db')
    c = conn.cursor()
    c.execute("SELECT meaning FROM words WHERE word=?", (word,))
    existing_word = c.fetchone()
    
    if existing_word:
        conn.close()
        return existing_word[0]
    else:
        api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            meaning = data[0]['meanings'][0]['definitions'][0]['definition']
            models.add_word_to_database(word, meaning)
            conn.close()
            return meaning
        else:
            conn.close()
            return "Word not found"

def text_to_speech(text, filename):
    tts = gTTS(text=text, lang='en')
    audio_dir = os.path.join(app.root_path, 'static', 'audio')
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    audio_path = os.path.join(audio_dir, f"{filename}.mp3")
    tts.save(audio_path)
    return url_for('static', filename=f"audio/{filename}.mp3")

def generate_audio_for_word_and_meaning(word, meaning):
    word_audio_path = text_to_speech(word, f"{word}_pronunciation")
    meaning_audio_path = text_to_speech(meaning, f"{word}_meaning")
    return word_audio_path, meaning_audio_path

if __name__ == '__main__':
    models.init_db()
    app.run(debug=True)
