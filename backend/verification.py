from db_operations.db_operations import get_task  # pobiera dane zadania i szablon

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
        task_id, files = cursor.fetchone()
        # TU WYWOŁUJEMY NASZ MAGICZNY SPRAWDZACZ ZAMIAST TEGO
        score = 100.0
        message = "Stub: RABINI WYDALI WYROK"
        status = "completed"

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