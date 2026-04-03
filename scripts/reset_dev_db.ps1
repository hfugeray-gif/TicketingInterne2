Remove-Item -Force backend/app.db -ErrorAction SilentlyContinue
cd backend
python -m alembic upgrade head