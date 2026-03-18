FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "app:app", "--workers=1", "--threads=1", "--bind", "0.0.0.0:10000"]