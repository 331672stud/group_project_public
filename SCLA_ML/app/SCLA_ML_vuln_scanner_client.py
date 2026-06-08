"""
SCLA_ML_vuln_scanner_client.py

Biblioteka / klient do wykorzystania skonteneryzowanego modelu SCLA_ML_vuln_scanner.

Aby wykorzystać jako biblioteka:
    from SCLA_ML_vuln_scanner_client import VulnDetectorClient
    client = VulnDetectorClient()
    result = client.analyze("SELECT * FROM users WHERE id=" + user_input)
    print(result)

Aby wykorzystać z CLI:
    python vuln_detector_client.py --code "os.system(user_input)"
    python vuln_detector_client.py --file path/to/code.py
    python vuln_detector_client.py --interactive
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
import threading
import requests

#OLLAMA_BASE_URL = "http://localhost:11434" #TO JEST JAK SPRAWDZAMY Z HOSTA
OLLAMA_BASE_URL = "http://vuln-detector:11434" #to jest z kontenera 
MODEL_NAME = "SCLA_ML_vuln_scanner"

VALID_LABELS = [
    "SQL Injection",
    "Cross-Site Scripting (XSS)",
    "Command Injection",
    "Path Traversal",
    "Buffer Overflow",
    "Insecure Deserialization",
    "No Vulnerability",
]

INSTRUCTION = (
    "Analyze the following code and determine whether it contains a security vulnerability. "
    "If a vulnerability is present, state its exact type from this list: "
    "SQL Injection, Cross-Site Scripting (XSS), Command Injection, Path Traversal, "
    "Buffer Overflow, Insecure Deserialization. "
    "If no vulnerability is present, respond with: No Vulnerability."
)

@dataclass
class AnalysisResult:
    label:         str
    is_vulnerable: bool
    raw_output:    str
    latency_ms:    float

    def to_dict(self) -> dict:
        return {
            "label":         self.label,
            "is_vulnerable": self.is_vulnerable,
            "raw_output":    self.raw_output,
            "latency_ms":    round(self.latency_ms, 2),
        }

    def __str__(self) -> str:
        status = "VULNERABLE" if self.is_vulnerable else "CLEAN"
        return (
            f"Status:    {status}\n"
            f"Label:     {self.label}\n"
            f"Latency:   {self.latency_ms:.0f}ms\n"
            f"Raw:       {self.raw_output}"
        )


class VulnDetectorClient:
    """
    Klasa-klient dla skonteneryzowanego skanera wrażliwości.

    :param str base_url: URL serwera Ollama. Domyślnie OLLAMA_BASE_URL
    :param str model_name: Nazwa modelu Ollama. Domyślnie MODEL_NAME
    :param int timeout: Czas timeout'u zapytania w sekundach. Domyślnie: 60
    """

    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model_name: str = MODEL_NAME,
        timeout: int = 120,
        # keep_alive:bool = True,
        # ping_interval_s: int  = 120
    ):
        self.base_url   = base_url.rstrip("/")
        self.model_name = model_name
        self.timeout    = timeout
        self.session    = requests.Session()
        # if keep_alive:
        #     self._start_keep_alive(ping_interval_s)


    # def _start_keep_alive(self, interval: int) -> None:
    #     """
    #     Pętla co interval sekund, żeby model był wgrany w VRAM kontenera 
    #     """
    #     def ping_loop():
    #         while not self._stop_ping.wait(timeout=interval):
    #             try:
    #                 self.session.post(
    #                     f"{self.base_url}/api/chat",
    #                     json={
    #                         "model":    self.model_name,
    #                         "messages": [{"role": "user", "content": " "}],
    #                         "stream":   False,
    #                         "options":  {"num_predict": 1},
    #                     },
    #                     timeout=10,
    #                 )
    #             except Exception:
    #                 pass   # Silently ignore — main requests will surface real errors

    #     thread = threading.Thread(target=ping_loop, daemon=True)
    #     thread.start()

    
    def _build_prompt(self, code: str) -> str:
        """ 
        Towrzy prompt na podstawie kodu.

        :param str code: kod do analizy
        :return: str z instrukcją do LLM
        """
        return f"{INSTRUCTION}\n\n### Code:\n{code.strip()}\n\n### Response:"

    def _parse_label(self, raw: str) -> str:
        """
        Sprawdza opis zwrócony przez LLM.

        :param str raw: czysty zwrot z LLM
        :return: opis spośród tych opisanych w VALID_LABELS
        """
        raw_lower = raw.lower()
        for label in VALID_LABELS:
            if label.lower() in raw_lower:
                return label
        return "Unknown"


    def analyze(self, code: str) -> AnalysisResult:
        """
        Podstawowa funkcji analizy kodu.

        :param str code: Kod do analizy
        :return: AnalysisResult dla kodu
        :raises ConnectionError: If the Ollama server is unreachable.
        :raises RuntimeError: If the server returns an unexpected response.
        """

        prompt = self._build_prompt(code)
        start  = time.perf_counter()

        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json={
                    "model":  self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 20,
                    },
                },
                timeout=self.timeout,
            )
            response.raise_for_status()

        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot reach Ollama at {self.base_url}. "
                "Is the Docker container running? "
                "Try: docker compose up -d"
            )
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Ollama returned HTTP {response.status_code}: {e}")

        latency_ms = (time.perf_counter() - start) * 1000
        raw = response.json()["message"]["content"].strip()
        label = self._parse_label(raw)

        return AnalysisResult(
            label         = label,
            is_vulnerable = label != "No Vulnerability",
            raw_output    = raw,
            latency_ms    = latency_ms,
        )

    def analyze_file(self, path: str | Path) -> AnalysisResult:
        """
        Analiza wrażliwości dla pliku.

        :param str|Path path: ścieżka do pliku do analizy
        :return: wynik AnalysisResult dla pliku.

        """
        code = Path(path).read_text(encoding="utf-8")
        return self.analyze(code)

    def analyze_batch(self, snippets: list[str]) -> list[AnalysisResult]:
        """
        Analiza wielu kodów sekwencyjnie 

        :param list[str] snippets: lista str kodów, do przeanalizowania
        :return: lista AnalysisResult odpowiednia dla listy snippets

        """
        return [self.analyze(snippet) for snippet in snippets]

    def health_check(self) -> bool:
        try:
            response = self.session.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )
            response.raise_for_status()
            models = [m["name"] for m in response.json().get("models", [])]
            return any(self.model_name in m for m in models)
        except Exception:
            return False

    def wait_until_ready(self, timeout: int = 120, poll_interval: int = 3) -> None:
        deadline = time.time() + timeout
        print(f"Waiting for {self.base_url} to be ready...", end="", flush=True)

        while time.time() < deadline:
            if self.health_check():
                print(" ready.")
                return
            print(".", end="", flush=True)
            time.sleep(poll_interval)

        raise TimeoutError(
            f"Ollama server not ready after {timeout}s. "
            "Check: docker compose logs vuln-detector"
        )



def _cli():
    parser = argparse.ArgumentParser(
        description="Vulnerability detector CLI — queries the containerised model."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--code",        type=str,  help="Code snippet as a string")
    group.add_argument("--file",        type=str,  help="Path to a source file")
    group.add_argument("--interactive", action="store_true",
                       help="Enter interactive mode — paste code, press Enter twice to submit")

    parser.add_argument("--url",    default=OLLAMA_BASE_URL, help="Ollama server URL")
    parser.add_argument("--model",  default=MODEL_NAME,      help="Model name")
    parser.add_argument("--json",   action="store_true",      help="Output as JSON")
    parser.add_argument("--wait",   action="store_true",
                        help="Wait for the server to be ready before querying")
    args = parser.parse_args()

    client = VulnDetectorClient(base_url=args.url, model_name=args.model)

    if args.wait:
        client.wait_until_ready()

    if args.code:
        result = client.analyze(args.code)
        print(json.dumps(result.to_dict(), indent=2) if args.json else str(result))

    elif args.file:
        result = client.analyze_file(args.file)
        print(json.dumps(result.to_dict(), indent=2) if args.json else str(result))

    elif args.interactive:
        print("Interactive mode. Paste code and press Enter twice to analyze.")
        print("Type 'quit' to exit.\n")
        while True:
            lines = []
            try:
                while True:
                    line = input()
                    if line.lower() == "quit":
                        sys.exit(0)
                    if line == "" and lines:
                        break
                    lines.append(line)
            except EOFError:
                break

            code = "\n".join(lines)
            if not code.strip():
                continue

            result = client.analyze(code)
            print("\n" + ("─" * 40))
            print(json.dumps(result.to_dict(), indent=2) if args.json else str(result))
            print("─" * 40 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        _cli()
    else:
        # Run built-in examples when called with no arguments
        client = VulnDetectorClient()

        if not client.health_check():
            print("ERROR: Ollama server not reachable.")
            print("Start the container first: docker compose up -d")
            sys.exit(1)

        test_cases = [
            (
                "SQL Injection",
                'String q = "SELECT * FROM users WHERE name=\'" + userInput + "\'";'
            ),
            (
                "Command Injection",
                "import os\nos.system('ping ' + user_input)"
            ),
            (
                "Path Traversal",
                'filename = request.args.get("f")\nopen("/var/data/" + filename)'
            ),
            (
                "XSS",
                'document.getElementById("out").innerHTML = location.search;'
            ),
            (
                "Clean code",
                'stmt = conn.prepareStatement("SELECT * FROM users WHERE id = ?")\nstmt.setInt(1, userId)'
            ),
        ]

        print(f"{'─'*60}")
        print(f"  Vulnerability Detector — {len(test_cases)} test cases")
        print(f"{'─'*60}\n")

        correct = 0
        for expected_desc, code in test_cases:
            result = client.analyze(code)
            marker = "✓" if (
                (expected_desc == "Clean code") == (not result.is_vulnerable)
            ) else "✗"
            correct += marker == "✓"

            print(f"[{marker}] Expected: {expected_desc}")
            print(f"    Got:      {result.label}")
            print(f"    Latency:  {result.latency_ms:.0f}ms")
            print()

        print(f"Result: {correct}/{len(test_cases)} correct")
