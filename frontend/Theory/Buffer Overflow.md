# Buffer Overflow (przepełnienie buforu)

## Wstęp teoretyczny

**Buffer Overflow** (przepełnienie buforu) to jeden z najstarszych i zarazem najgroźniejszych typów podatności w oprogramowaniu. Atak ten dotyczy języków programowania, w których nie istnieje wbudowana
ochrona granic tablic i buforów w pamięci, pozwalających na manipulację pamięcią - takich jak **C** i **C++**.

W kontekście programowania w takich językach, *bufor* to obszar pamięci o określonej, z góry zdefiniowanej długości, przeznaczony do tymczasowego przechowywania danych. W kwestii ataku, aspekt przechowywania
tymczasowych danych nie jest istotny, jednak istotny jest fakt iż *użytkownik ma dostęp do zapisania wejścia w buforze*. 

**Przepełnienie buforu** następuje wtedy, gdy program zapisuje *więcej danych, niż bufor może pomieścić* - nadmiarowe bajty, które nie mieszczą się w odgórnym limicie danych, 
**zapisywane są w sąsiadujących obszarach pamięci**, co skutkuje *nadpisaniem danych tam przechowywanych*. W ten sposób można nadpisać dowolną liczbę bajtów danych, które są zapisane na stosie 
*po* podatnej strukturze.

Wyróżnia się pod-typy ataku przepełnienia buforu w zależności od jego celu. **Stack-based Buffer Overflow** nadpisuje dane na stosie, w tym adresu powrotu - może to spowodować powrót do innego miejsca w pamięci, więc
wykonanie dowolnej innej rzeczy w ramach programu. **Heap-based Buffer Overflow**, w przeciwieństwie, nadpisuje dane na stercie (heap), co często prowadzi do korupcji struktur zarządzania pamięcią.

Wykonując udany atak *Buffer Overflow*, atakujący jest w stanie m.in.:
- przejąć pełną kontrolę nad podatnym procesem;
- eskalować uprawnienia, jeśli proces działa z prawami administratora;
- wykonać dowolnego kodu, pod warunkiem że jest on zapisany w pamięci atakowanej maszyny (arbitrary code execution);
- destabilizować lub zakończyć działanie aplikacji.


Rozważmy prosty, podatny program w języku C:

```
#include <stdio.h>
#include <string.h>

void authenticate(char *input) {
    char buffer[64];
    strcpy(buffer, input);
    printf("Witaj: %s\n", buffer);
}

int main() {
    char user_input[256];
    gets(user_input); 
    authenticate(user_input);
    return 0;
}
```


W powyższym kodzie bufor *buffer* ma 64 bajty. Jeżeli użytkownik poda do *user\_input* ciąg dłuższy niż 64 znaki, nadmiarowe bajty zaczną nadpisywać sąsiednie obszary na stosie maszyny. 
Jednym z elementów potencjalnie nadpisanych jest **adres powrotu** - wartość wskazująca, gdzie program ma wrócić po zakończeniu funkcji. *Nadpisanie adresu powrotu* złośliwie spreparowaną 
wartością pozwala atakującemu przekierować przepływ wykonywania programu w dowolne miejsce, w celu wykonania dowolnego kodu, w tym do *shellcode'u* dostarczonego przez atakującego.


## Zabezpieczenia

Aby zabezpieczyć się przed przepełnieniem buforu w systemach należy trzymać się następujących zasad:

1. **Użycie bezpiecznych funkcji** - zastąpienie niebezpiecznych funkcji (w przykładzie *strcpy*, *gets*; ogółem - wszystkimi funkcjami manipulującymi pamięcią) wersjami sprawdzającymi 
    długość podanych ciągów bajtów (*str**n**cpy*, **f***gets*), oraz zabezpieczenie ostatniego bajtu ciągu jako `null`:

```
strncpy(buffer, input, sizeof(buffer) - 1);
buffer[sizeof(buffer) - 1] = '\0';
```

1. **Stack Canaries** - mechanizm kompilatora umieszczający specjalną, losową wartość, tzw. kanarka, pomiędzy buforami a adresem powrotu. Przed powrotem z funkcji
          sprawdzana jest zgodność tej wartości, a jeżeli jest niepoprawna - z uwagi na przepełnienie buforu lub inny problem - program jest niezwłocznie kończony. 
          Dla GCC, kanarki stosu można włączyć flagą  *-fstack-protector*;

2. **Address Space Layout Randomization** - mechanizm systemu operacyjnego losowo rozmieszczający w pamięci stos, stertę i biblioteki, utrudniając przewidzenie adresów do nadpisania. 
            Jest to metoda "bezpieczeństwa przez niejawność";

3. **Data Execution Prevention / No-Execute** - oznaczanie stron pamięci zawierających dane jako niewykonywalne. Metoda ta uniemożliwia wykonanie kodu powłokowego wstrzykniętego do buforu danych;

4. **Użycie języków z automatycznym zarządzaniem pamięcią** - języki takie jak Java, Python czy Rust eliminują lub znacznie ograniczają tego typu podatności. Jesto to spowodowane dzięki sprawdzaniu 
            granic tablic w czasie wykonywania (bounds checking).


## Dodatkowa literatura
1. https://owasp.org/www-community/vulnerabilities/Buffer_Overflow
2. https://en.wikipedia.org/wiki/Buffer_overflow
3. https://sekurak.pl/tag/buffer-overflow/