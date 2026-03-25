FROM python:latest

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "api_endpoints:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]