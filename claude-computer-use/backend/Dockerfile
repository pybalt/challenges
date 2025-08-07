FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app/backend

COPY ../computer_use_demo /app/computer_use_demo

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]