FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py", "--base-api-url", "http://127", "--client-id", "test", "--client-secret", "test"]
