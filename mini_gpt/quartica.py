from flask import Flask
from routes import gpt
from db import create_tables

app = Flask(__name__)
app.secret_key = "surya"
app.register_blueprint(gpt)

@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Create the app function to be used by gunicorn
def create_app():
    create_tables()  # Ensure your DB setup is called when the app is created
    return app

if __name__ == "__main__":
    # Only run app in dev mode if this is executed locally
    app.run(debug=True)
