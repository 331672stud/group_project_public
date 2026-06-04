# Platforma nauki cyberbezpieczeństwa – Backend

Aplikacja serwerowa wspomagająca naukę cyberbezpieczeństwa poprzez rozwiązywanie praktycznych zadań programistycznych. Backend udostępnia REST API, zarządza użytkownikami (logowanie przez USOS), kursami, zadaniami oraz zgłoszeniami rozwiązań.

## Architektura kontenerowa

Projekt uruchamiany jest za pomocą `docker compose` i składa się z trzech serwisów:

| Serwis | Opis |
|--------|------|
| `web`  | Serwer **FastAPI** (Python 3.12+), nasłuchuje na porcie `8000`. Zawiera całą logikę backendu. (tymczasowe) |
| `db`   | **PostgreSQL** (najnowszy obraz), dane przechowywane w wolumenie `postgres_data`. Schemat inicjowany automatycznie z `database/init.sql`. |
| `dev`  | Opcjonalny kontener deweloperski z **VS Code Server** (`code-server`), dostępny przez przeglądarkę na porcie `8443`. Hasło: `dev`. |

Komunikacja między kontenerami odbywa się w wewnętrznej sieci Dockera. Backend łączy się z bazą przez URL `postgresql://postgres:password@db:5432/postgres`.

## Wymagania wstępne

- [Docker](https://docs.docker.com/get-docker/) oraz [Docker Compose](https://docs.docker.com/compose/install/).
- Plik **`.env`** w głównym katalogu projektu (szczegóły poniżej).
- **FOLDER `frontend/` Z PLIKIEM `Dockerfile` KTÓREGO NIE MOGĘ CI ZPR'OWAĆ BO NIE JESTEM KOLABORANTEM** – docker compose oczekuje, że cały frontend znajduje się w katalogu `frontend/` (na tym samym poziomie co `backend/` i `database/`).
