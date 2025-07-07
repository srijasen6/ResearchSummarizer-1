# Complete Setup Guide for AI Research Assistant

This guide will help you set up and run the AI Research Assistant on your laptop using VSCode, even if you're new to programming.

## Prerequisites

Before starting, make sure you have:
- A Windows, macOS, or Linux computer
- At least 4GB of RAM (8GB+ recommended)
- At least 2GB of free storage space
- Internet connection for downloading dependencies

## Step 1: Install Required Software

### 1.1 Install Python

1. **Download Python 3.11+**:
   - Go to [python.org](https://www.python.org/downloads/)
   - Download Python 3.11 or newer
   - **CRITICAL**: During installation, check "Add Python to PATH"

2. **Verify Installation**:
   - Open Command Prompt (Windows) or Terminal (macOS/Linux)
   - Type: `python --version`
   - You should see "Python 3.11.x" or newer

### 1.2 Install Visual Studio Code

1. **Download VSCode**:
   - Go to [code.visualstudio.com](https://code.visualstudio.com/)
   - Download and install for your operating system

2. **Install Python Extension**:
   - Open VSCode
   - Click Extensions icon (or press Ctrl+Shift+X)
   - Search for "Python"
   - Install the Microsoft Python extension

### 1.3 Install Git (Optional but Recommended)

1. **Download Git**:
   - Go to [git-scm.com](https://git-scm.com/)
   - Download and install for your operating system

## Step 2: Download the Project

### Option A: Using Git (Recommended)
```bash
git clone <your-repository-url>
cd ai-research-assistant
```

### Option B: Download ZIP File
1. Download the project as a ZIP file from your repository
2. Extract it to a folder like `C:\ai-research-assistant` (Windows) or `~/ai-research-assistant` (macOS/Linux)
3. Open Command Prompt/Terminal and navigate to the folder:
   ```bash
   cd C:\ai-research-assistant  # Windows
   # or
   cd ~/ai-research-assistant   # macOS/Linux
   ```

## Step 3: Open Project in VSCode

1. **Open VSCode**
2. **Open the Project Folder**:
   - Click "File" → "Open Folder"
   - Navigate to your `ai-research-assistant` folder
   - Click "Select Folder"

3. **Open Terminal in VSCode**:
   - Press `Ctrl+`` (backtick) or go to "Terminal" → "New Terminal"
   - This opens a terminal at the bottom of VSCode

## Step 4: Install Dependencies

In the VSCode terminal, run these commands one by one:

### 4.1 Upgrade pip (package installer)
```bash
python -m pip install --upgrade pip
```

### 4.2 Install required packages
```bash
pip install flask flask-sqlalchemy gunicorn PyPDF2 numpy psycopg2-binary email-validator werkzeug sqlalchemy
```

**Note**: The AI models (sentence-transformers, llama-cpp-python, etc.) are optional. The app works with fallback implementations if they're not installed. To install them later on a powerful computer:
```bash
pip install sentence-transformers llama-cpp-python faiss-cpu torch transformers
```

## Step 5: Set Up Environment

### 5.1 Create uploads folder
```bash
mkdir uploads
mkdir models_cache
```

### 5.2 Set environment variables (Optional)
Create a file called `.env` in your project folder with:
```
SESSION_SECRET=your-secret-key-here
DATABASE_URL=sqlite:///research_assistant.db
```

## Step 6: Run the Application

### 6.1 Start the server
In the VSCode terminal, run:
```bash
python main.py
```

You should see output like:
```
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:5000
```

### 6.2 Open in Browser
1. Open your web browser
2. Go to: `http://localhost:5000`
3. You should see the AI Research Assistant homepage!

## Step 7: Using the Application

### Upload a Document
1. Click the upload area or drag & drop a PDF or TXT file
2. Wait for processing (you'll see a summary)
3. Choose "Ask Anything" or "Challenge Me" mode

### Ask Questions
1. Type questions about your document
2. Get answers with justifications and source references

### Challenge Mode
1. Click "Generate Questions" to get AI-generated comprehension questions
2. Answer them and get scored feedback

## Troubleshooting

### Common Issues

**1. "python: command not found"**
- Python not installed or not in PATH
- Try `python3` instead of `python`
- Reinstall Python with "Add to PATH" checked

**2. "Permission denied" errors**
- On macOS/Linux, try: `sudo pip install flask`
- Or use: `pip install --user flask`

**3. "Port 5000 already in use"**
- Change port in `main.py`: `app.run(host='0.0.0.0', port=5001, debug=True)`
- Or kill the process using port 5000

**4. Dependencies fail to install**
- Update pip: `python -m pip install --upgrade pip`
- Try installing one by one: `pip install flask`

**5. Application won't start**
- Check for error messages in terminal
- Ensure you're in the correct directory
- Verify all files are present

### Windows-Specific Commands

If you're on Windows and `python` doesn't work, try:
```cmd
py -3 main.py
# or
python3 main.py
```

### macOS/Linux-Specific Commands

You might need to use `python3` and `pip3`:
```bash
python3 -m pip install flask
python3 main.py
```

## Development Mode

For development (auto-restart when files change):
```bash
python main.py
```

The app runs in debug mode by default, so it will restart automatically when you make changes to the code.

## Next Steps

1. **Test with sample documents**: Try uploading a research paper or article
2. **Explore API endpoints**: Use the provided Postman collection
3. **Customize**: Modify templates and styling as needed
4. **Deploy**: Consider deploying to a cloud service for others to use

## File Structure
```
ai-research-assistant/
├── main.py                 # Application entry point
├── app.py                  # Flask app configuration
├── models.py               # Database models
├── routes.py               # API endpoints
├── services/               # Core business logic
│   ├── ai_service.py       # AI processing
│   ├── document_processor.py  # PDF/TXT handling
│   └── vector_store.py     # Search functionality
├── templates/              # HTML templates
├── static/                 # CSS, JS, images
├── uploads/                # Uploaded documents
├── models_cache/           # AI model cache
└── postman_collection.json # API testing
