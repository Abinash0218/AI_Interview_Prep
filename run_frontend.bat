@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
set BACKEND_URL=http://localhost:8000
streamlit run frontend/app.py --server.port 8501
