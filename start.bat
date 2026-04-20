@echo off
echo ==========================================
echo    Palaiziet "Tris Labas Lietas"
echo ==========================================

echo [1/2] Saku backend (Python Flask)...
cd backend
start "Backend - Flask" cmd /k "python app.py"
cd ..

echo [2/2] Saku frontend (Vite)...
cd frontend
start "Frontend - Vite" cmd /k "npm run dev"
cd ..

echo ==========================================
echo Lietotne tiek palaista! 
echo Backend darbosies uz: http://localhost:5000
echo Frontend darbosies uz: http://localhost:5173 (parasti)
echo ==========================================
pause
