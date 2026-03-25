FROM python:latest

RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["fastapi", "run", "app:app", "--host", "0.0.0.0", "--port", "8000"]