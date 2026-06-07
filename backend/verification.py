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
    Stub funkcji sprawdzającej. Po zakończeniu aktualizuje submission_results.
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
        cursor.execute("SELECT task_id, content FROM submissions WHERE id=%s", (submission_id,))
        task_id, content_json = cursor.fetchone()
        
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

        # Ustal wynik końcowy
        if vulnerabilities:
            # Jeśli znaleziono jakąkolwiek podatność – obniżamy score do 0
            score = 0.0
            status = "completed"
            vuln_list = ', '.join([f"{v['file']}: {v['label']}" for v in vulnerabilities])
            message = f"Znaleziono podatności: {vuln_list}"
        else:
            score = 100.0
            status = "completed"
            message = "Brak wykrytych podatności. Kod jest bezpieczny."

        cursor.execute(
            """UPDATE submission_results 
               SET status=%s, score=%s, message=%s, checked_at=NOW() 
               WHERE submission_id=%s""",
            (status, score, message, submission_id)
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