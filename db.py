import mysql.connector
from datetime import datetime
import time
from flask_login import current_user
from dotenv import load_dotenv
import os

load_dotenv()

print("DB_HOST =", os.getenv("DB_HOST"))
print("DB_USER =", os.getenv("DB_USER"))

def get_connection():
    for _ in range(10):  # Try 10 times
        try:
            return mysql.connector.connect(
                host=os.getenv("DB_HOST", "db"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME"),
                ssl_ca="DigiCertGlobalRootCA.crt.pem"
            )
        except mysql.connector.errors.InterfaceError:
            print("DB not ready, waiting...")
            time.sleep(3)
    raise Exception("DB not ready after many attempts")
def create_tables():
    con = get_connection()
    cursor = con.cursor()
    #create signup table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signup (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            chat_id VARCHAR(255) PRIMARY KEY,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id INT NOT NULL,
            title TEXT,
            FOREIGN KEY (user_id) REFERENCES signup(user_id) ON DELETE CASCADE
        )
    ''')

    # Create chats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chat_id VARCHAR(255),
            user_input TEXT,
            gpt_response TEXT,
            FOREIGN KEY (chat_id) REFERENCES chat_sessions(chat_id) ON DELETE CASCADE
        )
    ''')

    con.commit()
    con.close()



# Insert new session
def create_chat_session(chat_id, user_id, title=None):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute(
        "INSERT INTO chat_sessions (chat_id, title, user_id) VALUES (%s, %s, %s)",
        (chat_id, title, user_id)
    )
    con.commit()
    con.close()

# Insert a chat message
def insert_chat(chat_id, user_input, gpt_response):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute(
        "INSERT INTO chats (chat_id, user_input, gpt_response) VALUES (%s, %s, %s)",
        (chat_id, user_input, gpt_response)
    )
    con.commit()
    con.close()

# Fetch all chats for one session
def fetch_all_chats(chat_id):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute(
        "SELECT user_input, gpt_response FROM chats WHERE chat_id = %s",
        (chat_id,)
    )
    chats = [{'user': row[0], 'gpt': row[1]} for row in cursor.fetchall()]
    con.close()
    return chats

# Fetch all previous chat sessions
def fetch_all_sessions(user_id):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute(
        "SELECT chat_id, created_at, title FROM chat_sessions WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    sessions = [{'chat_id': row[0], 'created_at': row[1], 'title': row[2]} for row in cursor.fetchall()]
    con.close()
    return sessions


# insert into signup table
def insert_signup(email, password):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute(
        "insert into signup(email, password) values(%s, %s)",
        (email, password)
    )
    con.commit()
    con.close()

    #checking if user exits are not 
def user_exists(email):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("select * from signup where email=%s",(email,))
    result = cursor.fetchone()
    con.close()
    return result is not None
# method to delete the session
def delete_session(chat_id):
    con = get_connection()
    cursor= con.cursor()
    cursor.execute("delete from chat_sessions where chat_id=%s",
                (chat_id,)
             )
    con.commit()
    con.close()
#method to get the user_id
def get_user_id_by_email_password(email, password):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("SELECT user_id FROM signup WHERE email=%s AND password=%s", (email, password))
    result = cursor.fetchone()
    con.close()
    return result[0] if result else None

# method to check the chat session is exits are not 
def chat_session_exists(chat_id):
    con = get_connection()
    cursor = con.cursor()
    cursor.execute("SELECT 1 FROM chat_sessions WHERE chat_id = %s", (chat_id,))
    exists = cursor.fetchone() is not None
    con.close()
    return exists
