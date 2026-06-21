## Wstęp teoretyczny
W przestrzeni cyberataków, jednym z najbardziej znanych, częstych metod ataku są ataki typu *Code Injection* - wstrzyknięcie kodu.
W 2025 roku, ataki typu *Code Injection* zajęły 5 miejsce na liście najczęstszych ataków OWASP Top 10: [https://owasp.org/Top10/2025/](https://owasp.org/Top10/2025/).
 W poprzednich latach, *Code Injection* również zajmowało wysokie notowania na tej liście.


Ataki wstrzyknięcia kodu wykorzystują lukę w kodzie źródłowym podatnych programów, która pozwala na wysłanie wkładu (user input / payload)  
przez niezaufanego użytkownika do interpretera aplikacji.  

W przypadku normalnego, planowanego wykorzystania kodu interpreter bezproblemowo spełnia funkcję, którą miał wykonać.
Przykładowo, wyobraźmy sobie okno logowania do systemu, w które użytkownik może podać login i hasło. Wpisanie odpowiednich danych,
tj. loginu i hasła użytkownika (zarejestrowanego lub nie) sprawi, że system zachowa się tak, jak oczekiwano - zaloguje użytkownika lub
wykona operację, którą miał wykonać gdy podane informacje są niezgodne.
Natomiast, jeżeli wejście od użytkownika zawiera *złośliwy kod, znaki specjalne lub niezaufane dane*, przekazanie ich 
do interpretera może sprawić, że atakujący zmieni działanie potencjalnie całego systemu na swoją korzyść.

Udane ataki *Code Injection* są w stanie m.in. 
- wykraść dane z bazy systemu;
- dać niepożądany dostęp do krytycznych części systemu komputerowego;
- pozwolić na wgranie malware'u - złośliwego kodu - do systemu. 

Najpopularniejszym, a zarazem najprostszym przykładem ataku typu *Code Injection* jest **SQL Injection**.
Jak nazwa wskazuje, atak ten wykorzystuje nieodpowiednie zabezpieczenia aplikacji wykorzystującym bazy danych SQL, 
co tworzy wektor ataku do, potencjalnie, całej bazy danych danego systemu. Wykorzystanie takiego wektora może spowodować
wykradnięcie danych, usunięcie lub zmiana wartości kluczowych tabel z systemu i inne rozbicia systemu.

W przypadku **SQL Injection**, interpreterem wstrzyknięcia jest interpreter składni języka SQL, a wektorem ataku - wrażliwy
kod obsługujący ten interpreter i wykonujący zapytania z wkładem użytkownika.

Korzystając z wcześniejszego przykładu okna logowania, oraz załóżmy że posiadamy aplikację obsługującą SQL w języku Python.
Wyobraźmy sobie sytuację w której mamy dwie zmienne - `username` i `password`, których wartości są pobierane od 
użytkownika poprzez wpisanie ich w ekranie logowania. Następnie, w celu sprawdzenia czy użytkownik istnieje i czy jego 
informacje poświadczające się zgadzają, wykonywany jest następujący kod:

```
var query = "SELECT * FROM users WHERE name = '" + username + "'"
response = sql.execute(query)
```

Na papierze, kod wygląda dobrze - podanie nazwy użytkownika sprawi, że w bazie zostaną wyszukane dane tylko o użytkowniku `username` - dla tekstu *user1* zapytanie ma postać:
```
SELECT * FROM users WHERE name = '**user1**'
```

Natomiast, wyobraźmy sobie sytuację w której atakujący podaje wartość *user1' OR '123'='123*. Wówczas, zapytanie ma postać:
```
SELECT * FROM users WHERE name = '**user1' OR '123' = '12**'
```

Grubą czcionką zaznaczono wejście od atakującego. Zwykła czczionka to część stała zmiennej query.

W tej sytuacji, atakujący wykorzystał nieodpowiednie filtrowanie danych wejściowych w celu wyświetlenia **wszystkich** rekordów bazy
*users* poprzez wprowadzenie złośliwego kodu - warunku, który jest zawsze prawdziwy (tekst "123" zawsze jest równy tekstowi "123", 
więc warunek wyszukiwania jest spełniony dla każdego rekordu - zapytanie zwraca każdy rekord).

Co więcej, w niefiltrowane wejście można wprowadzić *dowolny złośliwy kod, wpływający na bazę danych do której serwis ma dostęp* - 
wystarczy użyć znak zakończenia komendy (najczęściej *;*), po czym wprowadzić zupełnie nową komendę, na przykład:
1. DROP TABLE xyz;
2. SELECT * FROM xyz WHERE 't' = 't 

## Zabezpieczenia

Zabezpieczenia przed atakami typu *Code Injection* sprowadzają się do następujących, kluczowych parametrów:
1. **Parametryzacja danych** - pre-kompilacja kodu oraz wprowadzenie danych od użytkownika do istniejącego stwierdzenia; 
2. **Sanityzacja - wykorzystanie Whitelist słów kluczowych** - ograniczenie możliwych słów kluczowych do tych, które są bezpieczne, i odrzucanie pozostałych;
3. **Wykorzystanie reguły Principle of Least Privilege** - użytkownik, proces, zadanie czy program w systemie powinno mieć 
            tylko i wyłącznie najmniejszy możliwy poziom dostępu do wykonania swojej funkcji.


W zadaniach skupimy się głównie na parametryzacji danych wejściowych, gdyż jest to najbardziej kluczowe zabezpieczenie w przypadku kodu
*SQL Injection*. Oczywiście pozostałe zabezpieczenia również należy stosować, nie tylko przy atakach typu *Code Injection*.

Parametryzacja kodu SQL polega na podzieleniu części "kodu" oraz części "danych" na dwie, oddzielne strefy.
Część "kodu" jest kompilowana *przed* dodaniem do niej części "danych", co pozwala na zachowanie jednej, spójnej dyrektywy
niezależnie od tego jakie jest wejście podane przez użytkownika - wszystkie znaki specjalne, złośliwy kod nie są interpretowane 
jako część kodu do wykonania, a jako zmienne zamknięte w parametrach klauzul. 

Korzystając z poprzedniego przykładu, parametryzacja w języku SQL sprowadza się do wprowadzenia znaku *(?)* w miejsce, gdzie będzie
część "danych". (Kilka zmiennych może być podawane jako (?,?,...,?)) Parametryzacja kodu powyżej powinna wyglądać w następujący 
sposób:
```
var query = "SELECT * FROM users WHERE name = (?)"
response = sql.execute(query, username)
```

Wówczas, część *SELECT * FROM users WHERE name = (?)* jest częścią "kodu", kompilowaną wcześniej. *username* jest częścią "danych",
podaną w wyznaczone na to miejsce - znak zapytania.

Teraz, niezależnie od podanych przez użytkownika zmiennych typu string, zostaną one potraktowane tylko jako wejście do wyfiltrowania - 
nie kod wykonywalny. W praktyce stwierdzenie wyglądało by następująco:
```
SELECT * FROM users WHERE name = ('user1') 
SELECT * FROM users WHERE name = ('user1; drop table xyz;')
```

## Dodatkowa literatura 
1. [https://owasp.org/Top10/2025/A05_2025-Injection/](https://owasp.org/Top10/2025/A05_2025-Injection/)
2. [https://owasp.org/www-community/attacks/SQL_Injection](https://owasp.org/www-community/attacks/SQL_Injection)
3. [https://sekurak.pl/czym-jest-sql-injection/](https://sekurak.pl/czym-jest-sql-injection/)
4. [https://pl.wikipedia.org/wiki/SQL_injection](https://pl.wikipedia.org/wiki/SQL_injection)
