FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements-render.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend/app /app/backend/app
COPY ml/models/random_forest_v4.pkl /app/ml/models/random_forest_v4.pkl
COPY ml/data/processed/epl_matches.csv /app/ml/data/processed/epl_matches.csv

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--app-dir", "backend", "--host", "0.0.0.0", "--port", "8080"]
