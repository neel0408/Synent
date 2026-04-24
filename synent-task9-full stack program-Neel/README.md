# Flask Task Manager

A simple Flask + SQLite task manager web application with authentication, session handling, and responsive UI.

## Features
- User registration and login
- Session handling with Flask sessions
- Task creation, editing, deletion, and completion status
- SQLite database for users and tasks
- Responsive HTML/CSS frontend

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   python app.py
   ```
3. Open `http://127.0.0.1:5000` in your browser.

## Notes
- The database file is created automatically on first run.
- Change the secret key by setting `FLASK_SECRET_KEY` in your environment for production.
