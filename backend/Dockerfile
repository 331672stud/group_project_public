FROM python:latest

WORKDIR /app

COPY requirements.txt .

# copy and fix entrypoint script (ensure LF line endings and executable)
# entrypoint is located in ./backend/entrypoint.sh relative to build context
COPY ./backend/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

RUN pip install --no-cache-dir --upgrade -r requirements.txt

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "api_endpoints:app", \
    "--worker-class", "uvicorn.workers.UvicornWorker", \
    "--bind", "0.0.0.0:8000", \
    "--workers", "4", \
    "--access-logfile", "-", \
    "--error-logfile", "-"]
#CMD ["uvicorn", "api_endpoints:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--reload"] 