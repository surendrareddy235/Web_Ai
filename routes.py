from flask import Blueprint, request, session, render_template, redirect, url_for
from core_ai import ask_gemini
from db import (
    fetch_all_chats, insert_chat, create_chat_session,
    fetch_all_sessions, insert_signup, user_exists, delete_session,
    get_user_id_by_email_password, chat_session_exists
)
import uuid


gpt = Blueprint("mini_gpt", __name__)

@gpt.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@gpt.route("/")
def showindex():
    # Always clear both to reset session cleanly
    session.pop('user_id', None)
    session.pop('chat_id', None)
    session.clear() 

    return render_template('index.html', chat_history=[], all_sessions=[])


@gpt.route('/gemini', methods=['POST'])
def showopenai():
    user_id = session.get('user_id')

    if not user_id:
        return render_template('login.html')
    chat_id = session.get('chat_id')
    if not chat_id:
        chat_id = str(uuid.uuid4())
        session['chat_id'] = chat_id
    user_input = request.form.get("questionbox")


    if chat_id and user_id and not chat_session_exists(chat_id):
        create_chat_session(chat_id, user_id)

    if user_input and chat_id:
        response = ask_gemini(user_input)
        insert_chat(chat_id, user_input, response)

    chat_history = fetch_all_chats(chat_id)
    all_sessions = fetch_all_sessions(user_id) if user_id else []
    return render_template('index.html', chat_history=chat_history, all_sessions=all_sessions)


@gpt.route("/chat/<chat_id>")
def show_chat(chat_id):
    session['chat_id'] = chat_id
    user_id = session.get('user_id')
    chat_history = fetch_all_chats(chat_id)
    all_sessions = fetch_all_sessions(user_id) if user_id else []
    return render_template('index.html', chat_history=chat_history, all_sessions=all_sessions)


@gpt.route('/signup')
def showsignup():
    return render_template("signup.html")


@gpt.route('/login')
def showlogin():
    return render_template("login.html")


@gpt.route("/signupform", methods=['POST'])
def signupform():
    email = request.form.get("email")
    password = request.form.get("password")

    if user_exists(email):
        return render_template('signup.html', message='User already exists, please login.')

    try:
        insert_signup(email, password)
        return render_template('login.html')
    except Exception as e:
        return render_template('signup.html', message=f"Signup failed: {str(e)}")



@gpt.route('/loginform', methods=['POST'])
def showloginform():
    email = request.form.get('email')
    password = request.form.get('password')

    user_id = get_user_id_by_email_password(email, password)

    if user_id:
        session['user_id'] = user_id
        session['email'] = email
        session.pop('chat_id', None)  # clear any old chat_id if present

        chat_history = []
        all_sessions = fetch_all_sessions(user_id)
        return render_template('index.html', chat_history=chat_history, all_sessions=all_sessions)
    else:
        return render_template('login.html', message='YOUR CREDENTIALS ARE WRONG.PLEASE')


@gpt.route("/delete/<chat_id>", methods=['POST'])
def showdelete_session(chat_id):
    delete_session(chat_id)

    if session.get('chat_id') == chat_id:
        session.pop('chat_id', None)

    user_id = session.get('user_id')
    return render_template('index.html', chat_history=[], all_sessions=fetch_all_sessions(user_id))

@gpt.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('mini_gpt.showlogin'))

@gpt.route('/newchat', methods=['GET'])
def shownewchat():
    session['chat_id'] = str(uuid.uuid4())
    user_id = session.get('user_id')
    if user_id:
        create_chat_session(session['chat_id'], user_id)
    return render_template('index.html', chat_history=[], all_sessions=fetch_all_sessions(user_id))