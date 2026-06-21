"""
Skrypt do testowania obciążeniowego endpointu REST.
Uruchomienie: python load_test.py [liczba_zapytań] [liczba_wątków]
Domyślnie: 100 zapytań, 100 wątków.
Endpoint: http://localhost:8000/public-tasks
"""

import sys
import time
import statistics
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def make_request(url):
    """Wykonuje pojedyncze żądanie GET i zwraca czas odpowiedzi (s) oraz kod statusu."""
    try:
        start = time.perf_counter()
        resp = requests.get(url, timeout=10)
        end = time.perf_counter()
        return end - start, resp.status_code
    except Exception as e:
        return None, str(e)

def run_load_test(url, num_requests=100, max_workers=100):
    print(f"Test obciążeniowy: {num_requests} zapytań na {url}")
    print(f"Maksymalna liczba równoczesnych połączeń: {max_workers}\n")

    start_total = time.time()
    times = []       # czasy udanych odpowiedzi (status 200)
    errors = []      # kody błędów lub wyjątki

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(make_request, url) for _ in range(num_requests)]
        for fut in as_completed(futures):
            elapsed, result = fut.result()
            if elapsed is not None and result == 200:
                times.append(elapsed)
            else:
                errors.append(result)

    end_total = time.time()
    total_duration = end_total - start_total

    if not times:
        print("Brak udanych odpowiedzi – wszystkie żądania zakończyły się błędem.")
        if errors:
            print("Przykładowe błędy:", errors[:5])
        return

    # Statystyki czasów odpowiedzi
    sorted_times = sorted(times)
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    median = statistics.median(sorted_times)
    p95 = sorted_times[int(0.95 * len(sorted_times))]
    p99 = sorted_times[int(0.99 * len(sorted_times))]

    #całkowita liczba udanych żądań podzielona przez czas trwania testu
    rps = len(times) / total_duration

    print("=== Wyniki ===")
    print(f"Liczba udanych odpowiedzi: {len(times)} / {num_requests}")
    print(f"Liczba błędów: {len(errors)}")
    print(f"Całkowity czas testu: {total_duration:.3f} s")
    print(f"Średni czas odpowiedzi: {avg_time:.3f} s")
    print(f"Minimalny czas: {min_time:.3f} s")
    print(f"Maksymalny czas: {max_time:.3f} s")
    print(f"Mediana: {median:.3f} s")
    print(f"Percentyl 95: {p95:.3f} s")
    print(f"Percentyl 99: {p99:.3f} s")
    print(f"RPS (requests per second): {rps:.2f}")

if __name__ == "__main__":
    # Domyślny endpoint - publiczna lista zadań (nie wymaga logowania)
    endpoint = "http://localhost:8000/public-tasks"

    num_req = 100
    workers = 100
    if len(sys.argv) > 1:
        num_req = int(sys.argv[1])
    if len(sys.argv) > 2:
        workers = int(sys.argv[2])

    run_load_test(endpoint, num_req, workers)