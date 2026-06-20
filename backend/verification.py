from db_operations.db_operations import get_task  # pobiera dane zadania i szablon
import sys
from pathlib import Path

# Dodaj katalog SCLA_ML/app do ścieżki Python
sys.path.append(str(Path(__file__).parent.parent / "verifier"))

from SCLA_ML_vuln_scanner_client import VulnDetectorClient

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = VulnDetectorClient()
    return _client

def check_submission(db, submission_id: int):
    """
    funkcja sprawdzająca. Po zakończeniu aktualizuje submission_results
    i ustawia status na 'done' jeśli wynik to 100.
    """
    cursor = db.cursor()
    try:
        # Oznacz jako 'processing'
        cursor.execute(
            "UPDATE submission_results SET status='processing' WHERE submission_id=%s",
            (submission_id,)
        )
        db.commit()

        # Pobierz dane zgłoszenia
        cursor.execute("SELECT user_id, task_id, content FROM submissions WHERE id=%s", (submission_id,))
        user_id, task_id, content_json = cursor.fetchone()
        
        client = _get_client()
        
        files_data = content_json 
        vulnerabilities = []
        for file_obj in files_data:
            file_path = file_obj.get("path")
            code = file_obj.get("content")
            if not code:
                continue
            result = client.analyze(code)
            if result.is_vulnerable:
                vulnerabilities.append({
                    'file': file_path,
                    'label': result.label,
                    'raw': result.raw_output
                })

        #Zapisz wynik
        if vulnerabilities:
            # Jeśli znaleziono błąd - 0
            score = 0.0
            status = "completed"
            vuln_list = ', '.join([f"{v['file']}: {v['label']}" for v in vulnerabilities])
            message = f"Znaleziono podatności: {vuln_list}"
        else:
            score = 100.0
            status = "completed"
            message = "Brak wykrytych podatności. Kod jest bezpieczny."

        # Aktualizacja submission_results
        cursor.execute(
            """UPDATE submission_results 
               SET status=%s, score=%s, message=%s, checked_at=NOW() 
               WHERE submission_id=%s""",
            (status, score, message, submission_id)
        )
        
        # Aktualizacja user_task_status tylko jeśli score == 100
        if score == 100.0:
            cursor.execute(
                """
                INSERT INTO user_task_status (user_id, task_id, status, last_viewed, content)
                VALUES (%s, %s, 'done', NOW(), %s::jsonb)
                ON CONFLICT (user_id, task_id) DO UPDATE
                    SET status = 'done', last_viewed = NOW(), content = EXCLUDED.content
                """,
                (user_id, task_id, content_json)
            )
        else:
            # Jeśli nie zaliczone, pozostawiamy jako 'in_progress'
            cursor.execute(
                """
                INSERT INTO user_task_status (user_id, task_id, status, last_viewed, content)
                VALUES (%s, %s, 'in_progress', NOW(), %s::jsonb)
                ON CONFLICT (user_id, task_id) DO UPDATE
                    SET last_viewed = NOW(), content = EXCLUDED.content
                """,
                (user_id, task_id, content_json)
            )
        
        db.commit()
    except Exception as e:
        cursor.execute(
            """UPDATE submission_results 
               SET status='error', message=%s, checked_at=NOW() 
               WHERE submission_id=%s""",
            (str(e), submission_id)
        )
        db.commit()
    finally:
        cursor.close()