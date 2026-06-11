# Command Injection
## Wstęp teoretyczny
Kontynuując trend ataków wstrzyknięcia, spojrzymy na trzeci popularny wektor ataku kategorii Injection: **Command Injection**, czyli wstrzyknięcie polecenia systemowego.
W tym wariancie wstrzyknięć zamiast języka zapytań bazodanowych czy skryptu wykonującego w przeglądarce, wektorem ataku jest *interpreter poleceń systemowych* danej powłoki (shell). 
Podatność ta pojawia się wówczas, gdy aplikacja *przekazuje dane wejściowe od użytkownika bezpośrednio do wywołania polecenia systemu operacyjnego*.
Jak można się domyśleć, w przypadkach zamierzonych nic złego nie musi się stać, natomiast podatność ta może być *niezwykle niebezpieczna*, w zależności od poziomu dostępu 
na którym wykonywany jest kod.

Rozważmy przykładową aplikację webową w Pythonie, która wykonuje polecenie *ping* na własnym serwerze, na podany przez użytkownika adres IP:

```
import os
def ping_host(host):
    result = os.system("ping -c 1 " + host)
    return result
```

Dla normalnego użycia z wartością *192.168.1.1* wywołane zostanie zwykłe zapytanie ping:

```
ping -c 1 192.168.1.1
```

Atakujący jest jednak w stanie podać wartość, zawierającą kod inny niż wyłącznie adres do polecenia ping, za pomocą *separatorów poleceń systemowych*.
Poniżej opisano separatory wykorzystywane w powłokach systemów opartych o jądro Linux:

- *;* - sekwencyjne wykonanie poleceń;
- *\&\&* - wykonanie drugiego polecenia jeśli pierwsze się powiodło;
- *||* - wykonanie drugiego polecenia jeśli pierwsze się nie powiodło;
- *|* - pipe, przesłanie wyjścia pierwszego polecenia jako wejście drugiego;
- *\$(polecenie)* lub *`polecenie`* - podstawienie polecenia (command substitution).

Kontynuując przykład, atakujący podając na wejściu *192.168.1.1; cat /etc/passwd* spowoduje wykonanie:

```
ping -c 1 192.168.1.1; cat /etc/passwd
```

Polecenie to, poza ping, wyświetli informacje o wszystkich użytkownikach systemu.

Oczywiście *cat* to nie jest jedyne polecenie, które można wykorzystać - *Command Injection* pozwala na wykonanie **dowolnego polecenia w interpreterze podatnego systemu.**
Z tego względu, skutki udanych ataków *Command Injection* są **krytyczne** ze względu na bezpośredni dostęp do powłoki systemu operacyjnego. Konsekwencje obejmują m.in.:
- pełne przejęcie maszyny;
- usunięcie lub wykradzenie plików;
- instalację malware'u lub backdoor'a;
- dalsze ruchy boczne w sieci (lateral movement).


## Zabezpieczenia

Zabezpieczenia przez *Command Injection* w większości pokrywają się z innymi atakami *Code Injection*, jednak kluczowe jest ich nakreślenie:
1. **Unikanie wywołań powłoki systemowej** - najskuteczniejszym zabezpieczeniem jest kompletne zrezygnowanie z wywołań funkcji odwołujących się do 
            interpretera systemowego - w Python, np. *os.system()*, *exec()*, *shell=True*. Zamiast tego należy wykorzystać biblioteki realizujące
            tę samą, zamierzoną funkcję bez angażowania shell'a:
```
import subprocess

def ping_host(host):
    result = subprocess.run(
        ["ping", "-c", "1", host],
        capture_output=True,
        text=True
    )
    return result.stdout
```

Przekazanie argumentów jako *listy* (nie jako ciągu znaków) sprawia, że *host* jest traktowany jako jeden argument, a nie fragment kodu powłoki;

2. **Walidacja i sanityzacja wejścia** - użycie whitelist'y dopuszczalnych wartości lub wyrażeń regularnych sprawdzających format danych 
            pozwala na kontrolowanie tego, co użytkownik wprowadza do programu. Dla przykładu z IP można wykorzystać np. wyrażenia regularne do sprawdzenia 
            poprawności wejścia - wyłącznie adresów IP w formacie *X.X.X.X*:
```
import re

def is_valid_ip(host):
    pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    return re.match(pattern, host) is not None
```

3. **Wykorzystanie reguły Principle of Least Privilege** - uruchamianie aplikacji z minimalnymi uprawnieniami niezbędnymi do działania 
            tak, aby nawet udany atak miał ograniczony zasięg;

4. **Stosowanie sandboxingu** - izolacja procesów wykonujących zewnętrzne polecenia (np. kontenery Docker, chroot, seccomp). W wyniku, dostęp aktywującego 
            jest automatycznie ograniczony tym, że jest w środowisku odizolowanym od innych części systemu. Oczywiście, to rozwiązanie nie sprawia, że atakujący nie ma dostępu do zasobów kontenera.


## Dodatkowa literatura 
1. https://owasp.org/www-community/attacks/Command_Injection
2. https://en.wikipedia.org/wiki/Code_injection
3. https://sekurak.pl/tag/command-injection/

