# Quick Start - Terminal Commands

## Prerequisites
- Python 3.11+ installed
- VSCode installed

## Step-by-Step Commands

### 1. Open VSCode and Terminal
1. Open VSCode
2. Open project folder: File → Open Folder
3. Open terminal: `Ctrl+`` (backtick) or Terminal → New Terminal

### 2. Navigate to Project (if needed)
```bash
# Windows
cd C:\path\to\ai-research-assistant

# macOS/Linux
cd ~/path/to/ai-research-assistant
```

### 3. Install Dependencies
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install required packages
pip install flask flask-sqlalchemy gunicorn PyPDF2 numpy psycopg2-binary email-validator werkzeug sqlalchemy
```

### 4. Create Required Folders
```bash
mkdir uploads
mkdir models_cache
```

### 5. Run the Application
```bash
python main.py
```

### 6. Open in Browser
Go to: `http://localhost:5000`

## Alternative Commands (if 'python' doesn't work)

### Windows
```cmd
py -3 -m pip install flask flask-sqlalchemy gunicorn PyPDF2 numpy psycopg2-binary email-validator werkzeug sqlalchemy
py -3 main.py
```

### macOS/Linux
```bash
python3 -m pip install flask flask-sqlalchemy gunicorn PyPDF2 numpy psycopg2-binary email-validator werkzeug sqlalchemy
python3 main.py
```

## Troubleshooting Commands

### Check Python Version
```bash
python --version
# or
python3 --version
```

### Check if packages are installed
```bash
pip list | grep flask
```

### Kill process on port 5000 (if needed)
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

### Install packages with user permissions
```bash
pip install --user flask flask-sqlalchemy gunicorn PyPDF2 numpy psycopg2-binary email-validator werkzeug sqlalchemy
```

## Success Indicators

You'll know it's working when you see:
```
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:5000
[INFO] Booting worker with pid: XXXX
```

And these warnings are normal (the app uses fallback implementations):
```
WARNING: sentence-transformers not available, using fallback embedding
WARNING: llama-cpp-python not available, using fallback responses
```