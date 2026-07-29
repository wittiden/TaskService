FROM python:3.14-slim

WORKDIR /app

COPY requirements-prod.txt .

RUN pip install -r --no-cache-dir requirements-prod.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "app.main", "--uvicorn"]
