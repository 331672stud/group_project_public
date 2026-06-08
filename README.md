# Platforma nauki cyberbezpieczeństwa – Backend

Aplikacja serwerowa wspomagająca naukę cyberbezpieczeństwa poprzez rozwiązywanie praktycznych zadań programistycznych. Backend udostępnia REST API, zarządza użytkownikami (logowanie przez USOS), kursami, zadaniami oraz zgłoszeniami rozwiązań. Frontend oraz mechanizm automatycznej weryfikacji rozwiązań są rozwijane oddzielnie.

## Architektura kontenerowa

Projekt uruchamiany jest za pomocą `docker compose` i składa się z trzech serwisów:

| Serwis | Opis |
|--------|------|
| `web`  | Serwer FastAPI (Python 3.12+), nasłuchuje na porcie `8000`. Zawiera całą logikę backendu. |
| `db`   | PostgreSQL (najnowszy obraz), dane przechowywane w wolumenie `postgres_data`. Schemat inicjowany automatycznie z `database/init.sql`. |
| `dev`  | Opcjonalny kontener deweloperski z VS Code Server (`code-server`), dostępny przez przeglądarkę na porcie `8443`. Hasło: `dev`. |

Komunikacja między kontenerami odbywa się w wewnętrznej sieci Dockera. Backend łączy się z bazą przez URL `postgresql://postgres:password@db:5432/postgres`.

## skrypty testowe

add_task.py - po prostu dodaje proste zadanie z plikami.
check_db_contents.py - prosty dump co jest w bazie aby sprawdzić co się dodało.
add_task_submission_user.py - trochę bardziej skomplikowane dodawanie zadania z konkretnym zapisem.
populate_test_data.py - masowy skrypt wyżej, dodaje kilka wartości dla lepszego testu.

## Zaimplementowane funkcjonalności

### Autoryzacja przez USOS

- Logowanie za pomocą protokołu **OAuth 1.0a** (konta uczelniane PW).
- Endpointy: `/login` (przekierowanie), `/callback` (powrót z USOS).
- Sesje przechowywane w ciasteczkach, połączenie z bazą danych.

### Użytkownicy

- Automatyczne tworzenie konta użytkownika po pierwszym zalogowaniu (dane z USOS: imię, nazwisko, typ – student/pracownik).
- Endpoint `/profile` zwraca dane zalogowanej osoby.

### Kursy

- Pobieranie aktywnych kursów użytkownika z USOS (`/my-courses`).
- Przypisywanie zadań do kursów (`/courses/{course_id}/tasks`).
- **Backendowa funkcja tworzenia kursów** (w `db_operations`) – nie wystawiona jeszcze przez API.

### Zadania

- Publiczna lista wszystkich zadań (`/public-tasks`).
- Zadania przypisane studentowi (`/assigned_tasks`).
- lista wszystkich zadań (`/tasks`).
- Szczegóły zadania (opis, trudność, języki, tagi, drzewo plików startowych, ostatnie rozwiązanie) – `/tasks/{task_id}`.
- konkretnie oryginalne pliki zadania (`/tasks/{task_id}/files`).
- **Wewnętrzne CRUD dla zadań** (funkcje `create_task_with_files`, `update_task`, `delete_task`) – tworzenie/edycja/usuwanie zadań możliwe przez skrypt wewnętrzny (np. `scripts/add_task.py`), niedostępne z zewnątrz.
- System tagów (tematów) – `/topics`, filtrowanie zadań po tagach.

### Zgłoszenia (rozwiązania)

- Składanie wieloplikowych rozwiązań (`POST /tasks/{task_id}/submit`).
- Przechowywanie rozwiązań w formacie JSONB (drzewo plików z zawartością).
- Historia zgłoszeń użytkownika (`/submissions`).

### Weryfikacja rozwiązań (stub)

- Podczas składania rozwiązania tworzony jest wpis w tabeli `submission_results` ze statusem `queued`.
- Zaimplementowano **stub** funkcji `check_submission` (symuluje sukces – zawsze 100%).
- Docelowy mechanizm sprawdzania można podpiąć w miejsce tego stuba.
- Endpoint `/submissions/{submission_id}/result` pozwala odpytać wynik sprawdzania.

### Dodawanie zadań wewnętrznie (bez API)

- Funkcja `create_task_with_files` w `db_operations.py` umożliwia utworzenie zadania wraz z plikami startowymi i tagami.
- Przykładowy skrypt: `scripts/add_task.py`. Uruchamiasz go wewnątrz kontenera `web`:

  ```bash
  docker compose exec web python /app/scripts/add_task.py
  ```

- Dzięki temu możesz wgrać zadania podczas inicjalizacji środowiska, bez udostępniania takiej możliwości przez API.

### Bezpieczeństwo

- CORS ograniczony do adresu frontendu z `.env`.
- Middleware sesyjny (`SessionMiddleware`).
- Chronione endpointy wymagają poprawnej sesji (funkcja `get_current_user`).
- Obecnie brak limiterów żądań, sekret sesji ma domyślną wartość tylko w razie braku zmiennej – zalecane ustawienie w produkcji.

---

## Endpointy API (pogrupowane)

Wszystkie ścieżki podano względem adresu backendu.  

### Autoryzacja

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| GET | `/login` | Przekierowuje do logowania USOS (OAuth) |
| GET | `/callback` | Callback OAuth – wymiana tokenów, zapis użytkownika, przekierowanie do frontendu |

### Profil i kursy

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| GET | `/profile` | Imię, nazwisko, typ konta zalogowanego użytkownika |
| GET | `/my-courses` | Lista kursów użytkownika z bieżącego semestru (dane z USOS) |
| GET | `/courses/{course_id}/tasks` | Zadania przypisane do danego kursu |

### Zadania

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| GET | `/public-tasks` | Lista wszystkich zadań (tylko id i tytuł) – publiczne |
| GET  | `/tasks` | Lista zadań przypisanych zalogowanemu użytkownikowi |
| GET  | `/tasks/{task_id}` | Pełne szczegóły zadania (opis, trudność, pliki startowe, tagi, ostatnie zgłoszenie) |
| GET  | `/topics` | Lista dostępnych tagów (tematów) |
| GET | `/topics/{tag_id}/tasks` | Zadania filtrowane po wybranym tagu |

### Zgłoszenia i postęp

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| POST | `/tasks/{task_id}/submit` | Wysłanie rozwiązania (wieloplikowy JSON) – zwraca `submission_id` |
| GET | `/submissions` | Historia wszystkich zgłoszeń zalogowanego użytkownika |
| GET | `/tasks/{task_id}/submission` | Ostatnie zgłoszenie dla danego zadania |
| PATCH | `/tasks/{task_id}/progress` | Aktualizacja statusu zadania (`new`, `inProgress`, `done`) i czasu ostatniego wyświetlenia |

### Wyniki sprawdzania

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| GET | `/submissions/{submission_id}/result` | Wynik sprawdzania zgłoszenia (status, punkty, komunikat) |

> **Endpointy dla prowadzących** (zarządzanie zadaniami, kursami, przypisywanie) są zaimplementowane w warstwie backendowej (`db_operations.py`), ale **nie zostały jeszcze wystawione jako trasy HTTP**. Obecnie zadania można dodawać jedynie przez wewnętrzny skrypt.
