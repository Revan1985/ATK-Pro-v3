# ATK-Pro – Odbudowa Płytek Przodków
**Uwaga:** Ten projekt jest rozwijany, utrzymywany i wspierany w całości przez jedną osobę. Każda informacja zwrotna, zgłoszenie lub wkład są mile widziane, ale za rozwojem nie stoi żaden zespół ani struktura firmowa.
## Opis
ATK-Pro to zaawansowane narzędzie do rekonstrukcji, archiwizacji i przeglądania zeskanowanych obrazów i dokumentów genealogicznych z portalu Antenati. Projekt obsługuje wielojęzyczne zarządzanie i dystrybucję jako samodzielną aplikację dla systemu Windows.
## Główne funkcje
- Automatyczna rekonstrukcja obrazów z kafelków IIIF
- Obsługa wielojęzyczna (20 języków)
- Nowoczesny interfejs graficzny (Qt)
- Zbuduj samodzielny plik EXE i wielojęzyczny instalator
## Instalacja
1. Pobierz instalator ATK-Pro-Setup-v2.0.exe lub samodzielny plik wykonywalny ATK-Pro.exe z sekcji wydań.
1. Postępuj zgodnie z instrukcjami wyświetlanymi na ekranie, aby zakończyć instalację.
1. Uruchom ATK-Pro z menu Start lub z folderu instalacyjnego.
## Struktura projektu
- `src/` – Główny kod źródłowy (GUI, logika, moduły)
- `zasoby/` – Zasoby wielojęzyczne (przewodniki, szablony, materiały)
- `locales/` – Pliki tłumaczeń .ini dla każdego języka
- `docs_generali/` – Glosariusze, dokumentacja ogólna, roadmap
- `scripts/` – Skrypty do konserwacji, tłumaczenia, walidacji
- `tests/` – Testy automatyczne i pokrycia
- `dist/` – Wyjście kompilacji/instalatora
## Dokumentacja
- Dokumentacja historyczna i pogłębiona jest teraz zarchiwizowana w `docs_generali/archivio/`.
- Niniejszy plik README oraz plik `CHANGELOG.md` podsumowują stan i główne etapy projektu.
## Historia i rozwój
Projekt powstał jako ewolucja narzędzi do genealogii cyfrowej, z naciskiem na przejrzystość, archiwizację historyczną i wsparcie międzynarodowe. Każdy kamień milowy jest śledzony i dokumentowany w repozytorium.
## Kredyty
Rozwój i utrzymanie: Daniele Pigoli
Współpraca: patrz dziennik zmian i uwagi dotyczące wydania
## Dziennik zmian
Zapoznaj się z plikiem `docs_generali/CHANGELOG.md`, aby poznać najważniejsze nowości i kamienie milowe projektu.
Po szczegóły historyczne i pełne uwagi, patrz folder `docs_generali/archivio/`.

-----
## Obecny stan
- Wszystkie aktywne moduły zostały przetestowane z bezpośrednim i obronnym pokryciem
- Adnotacja z blokiem `# === Test coverage ===` w zweryfikowanych modułach
- Moduł main.py, mimo częściowego pokrycia (64%), został logicznie zweryfikowany jako koordynujący
### Następne kroki
- Przygotować v2.1 z ewolucją przyrostową i zaktualizowaną dokumentacją

✍️ Opracowane przez Daniele Pigoli – z zamiarem połączenia rygoru technicznego i pamięci historycznej.
