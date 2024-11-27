from flask import Flask, request, render_template, abort
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)

# Configuration
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
PORT = int(os.environ.get('PORT', 5000))
DATABASE = 'messages.db'

def init_db():
    """Initialize the SQLite database and create the messages table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         text TEXT NOT NULL,
         ip TEXT NOT NULL,
         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
    ''')
    conn.commit()
    conn.close()

def get_messages():
    """Retrieve all messages from the database."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT text, ip, timestamp FROM messages ORDER BY timestamp DESC')
    messages = [{'text': row[0], 'ip': row[1], 'timestamp': row[2]} for row in c.fetchall()]
    conn.close()
    return messages

@app.route('/', methods=['POST'])
def receive_text():
    text = request.form.get('text', '').strip()
    if not text:
        abort(400, description="Text cannot be empty")
    
    if len(text) > 1000:  # Limit text length
        abort(400, description="Text too long (max 1000 characters)")
        
    try:
        ip = request.remote_addr
        
        # Store in database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('INSERT INTO messages (text, ip) VALUES (?, ?)', (text, ip))
        conn.commit()
        conn.close()
        
        print(f"Received text: {text} from IP: {ip}")
        return 'Data received successfully', 200
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        abort(500, description="Internal server error")

@app.route('/', methods=['GET'])
def display_text():
    try:
        messages = get_messages()
        return render_template('index.html', received_data=messages)
    except Exception as e:
        print(f"Error retrieving messages: {str(e)}")
        abort(500, description="Internal server error")

@app.errorhandler(400)
def bad_request(e):
    return str(e), 400

@app.errorhandler(500)
def server_error(e):
    return str(e), 500

if __name__ == '__main__':
    init_db()  # Initialize database on startup
    app.run(
        host='127.0.0.1',  # Only accept local connections by default
        port=PORT,
        debug=DEBUG
    )
