import time
import psycopg2
from psycopg2 import pool
import os
from fastapi import HTTPException

# Parametry bazy
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "postgres")

# Globalna zmienna – zostanie zainicjowana przy starcie aplikacji
connection_pool = None

def init_pool():
    """Tworzy pulę połączeń. Wywołaj RAZ przy starcie FastAPI (event 'startup')."""
    global connection_pool
    for _ in range(30):
        try:
            connection_pool = pool.ThreadedConnectionPool(
                minconn=5,          # minimalna liczba połączeń w puli
                maxconn=20,         # maksymalna liczba połączeń
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            print("Pula połączeń zainicjowana.")
            return
        except psycopg2.OperationalError:
            print("Czekam na bazę danych...")
            time.sleep(1)
    raise Exception("Nie można połączyć się z bazą danych.")

def close_pool():
    """Zamyka pulę połączeń. Wywołaj przy zatrzymaniu aplikacji (event 'shutdown')."""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        print("Pula połączeń zamknięta.")

def get_connection(timeout = 5):
    """Pobiera połączenie z puli. Używane przez endpointy. Jeśli brak wolnych przez `timeout` sekund,
    rzuca wyjątkiem PoolError.
    """
    if not connection_pool:
        raise RuntimeError("Pula nie została zainicjowana.")
    try:
        return connection_pool.getconn(timeout)  # timeout w sekundach
    except pool.PoolError:
        raise HTTPException(status_code=503, detail="Serwer przeciążony – spróbuj później.")

def release_connection(conn):
    """Oddaje połączenie z powrotem do puli."""
    if connection_pool:
        connection_pool.putconn(conn)