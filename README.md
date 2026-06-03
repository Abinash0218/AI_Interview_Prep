# AI Interview Preparation Assistant

A production-ready AI-powered interview preparation platform with **Streamlit** frontend, **FastAPI** backend, **PostgreSQL** database, **Google Gemini** AI, and **Google OAuth** authentication.

## Features

- **4 AI Assistants**: Technical Interview, Coding Assessment, HR Interview, Non-Technical Skills
- **Authentication**: Email signup/login, forgot password, Google OAuth, JWT sessions
- **Chat Management**: New chat, rename, delete, search, export PDF/TXT, share
- **Themes**: Light/Dark mode with persistence
- **AI**: Google Gemini (primary) with Groq fallback

---

## Prerequisites (Windows)

| Software | Version | Download |
|----------|---------|----------|
| Python | 3.10+ | https://www.python.org/downloads/ |
| PostgreSQL | 14+ | https://www.postgresql.org/download/windows/ |
| Git (optional) | Latest | https://git-scm.com/download/win |

During Python installation, check **"Add Python to PATH"**.

---

## Step-by-Step Setup Guide

### Step 1: Open Project Folder

```powershell
cd C:\Users\abina\Sourcesys\AI_Interview_Preparation
```

### Step 2: Create Virtual Environment

```powershell
python -m venv venv
```

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Install and Configure PostgreSQL

1. Install PostgreSQL from the official website.
2. Remember the password you set for the `postgres` user.
3. Open **pgAdmin** or **psql** and create the database:

```sql
CREATE DATABASE interview_prep;
```

Or via command line:

```powershell
psql -U postgres -c "CREATE DATABASE interview_prep;"
```

### Step 5: Configure Environment Variables

Copy the example environment file:

```powershell
copy .env.example .env
```

Edit `.env` with your values:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/interview_prep
SECRET_KEY=generate-a-random-secret-key-here
JWT_SECRET=generate-another-random-jwt-secret
GEMINI_API_KEY=your-gemini-api-key
GROQ_API_KEY=optional-groq-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:8501
```

Generate random secrets (PowerShell):

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Run this twice for `SECRET_KEY` and `JWT_SECRET`.

### Step 6: Get Google Gemini API Key

1. Go to https://aistudio.google.com/apikey
2. Click **Create API Key**
3. Copy the key into `.env` as `GEMINI_API_KEY`

### Step 7: Set Up Google OAuth (Optional)

1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Navigate to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth client ID**
5. Application type: **Web application**
6. Authorized redirect URIs: `http://localhost:8501`
7. Copy **Client ID** and **Client Secret** to `.env`
8. Enable **Google+ API** or **Google Identity** services if prompted

### Step 8: Initialize Database Tables

With virtual environment activated:

```powershell
python database/init_db.py
```

You should see: `Database tables created successfully!`

### Step 9: Run the Backend (Terminal 1)

```powershell
cd C:\Users\abina\Sourcesys\AI_Interview_Preparation
.\venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Or double-click `run_backend.bat`.

Verify: open http://localhost:8000/health — should show `{"status":"healthy"}`.

API docs: http://localhost:8000/docs

### Step 10: Run the Frontend (Terminal 2)

Open a **new** terminal:

```powershell
cd C:\Users\abina\Sourcesys\AI_Interview_Preparation
.\venv\Scripts\Activate.ps1
$env:BACKEND_URL="http://localhost:8000"
streamlit run frontend/app.py --server.port 8501
```

Or double-click `run_frontend.bat`.

Open http://localhost:8501 in your browser.

### Step 11: Create Your Account

1. Open http://localhost:8501
2. Click **Sign Up** tab
3. Enter name, email, password (min 8 chars, uppercase, lowercase, digit)
4. Start chatting in any of the 4 interview tabs

---

## Project Structure

```
AI_Interview_Preparation/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings from .env
│   ├── auth/                # JWT, password hashing
│   ├── oauth/               # Google OAuth
│   ├── database/            # SQLAlchemy connection
│   ├── models/              # User, Chat, Message, Settings
│   ├── routers/             # API endpoints
│   ├── services/            # AI, chat, export services
│   ├── prompts/             # System prompts per assistant
│   └── schemas/             # Pydantic validation
├── frontend/
│   ├── app.py               # Streamlit main app
│   ├── components/          # Auth, chat, sidebar, profile
│   ├── utils/               # API client, session
│   └── styles/              # Custom CSS themes
├── database/
│   └── init_db.py           # Create tables script
├── logs/                    # Application logs
├── tests/                   # Unit tests
├── requirements.txt
├── .env.example
├── run_backend.bat
├── run_frontend.bat
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/signup | Register new user |
| POST | /auth/login | Email login |
| POST | /auth/google-login | Google OAuth |
| POST | /auth/forgot-password | Request password reset |
| POST | /auth/logout | Logout |
| GET | /profile | Get user profile |
| PUT | /profile | Update profile |
| POST | /chat | Send message & get AI response |
| GET | /chat/history | List all chats |
| GET | /chat/{id} | Get chat with messages |
| DELETE | /chat/{id} | Delete chat |
| PUT | /chat/{id}/rename | Rename chat |
| GET | /export/pdf/{id} | Download PDF |
| GET | /export/txt/{id} | Download TXT |
| GET | /export/share/{id} | Share chat JSON |

---

## Running Tests

```powershell
.\venv\Scripts\Activate.ps1
pytest tests/ -v
```

---

## Troubleshooting

### Cannot connect to backend

- Ensure Terminal 1 is running: `uvicorn backend.main:app --reload`
- Check `BACKEND_URL=http://localhost:8000` in frontend terminal
- Test: http://localhost:8000/health

### Database connection error

- Verify PostgreSQL service is running (Services → postgresql)
- Check `DATABASE_URL` password and database name in `.env`
- Ensure database `interview_prep` exists

### `ModuleNotFoundError: No module named 'backend'`

- Run commands from project root: `AI_Interview_Preparation/`
- Activate virtual environment first
- For uvicorn: `uvicorn backend.main:app --reload` (from project root)

### Gemini API errors

- Verify `GEMINI_API_KEY` in `.env`
- Check API quota at https://aistudio.google.com/
- Optional: set `GROQ_API_KEY` for fallback

### Google OAuth not working

- Redirect URI must be exactly `http://localhost:8501`
- Add test users in Google Cloud Console if app is in testing mode
- Set both `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`

### Password reset in development

- Forgot password returns a reset link in the API response (shown in UI)
- Use the link or token to reset password on the login page

### Port already in use

```powershell
# Find process on port 8000
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```

---

## Quick Reference Commands

```powershell
# Setup (one time)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your credentials
python database/init_db.py

# Run daily
# Terminal 1:
uvicorn backend.main:app --reload

# Terminal 2:
streamlit run frontend/app.py
```

---

## License

MIT License — free for educational and personal use.
