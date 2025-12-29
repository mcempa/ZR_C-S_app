# Dokumentacja Projektu Client-Server
Wygenerowano: 2025-01-26 18:59

## Struktura Projektu
```
src/
├── models/
│   └── user.py
├── config.py
├── services/
│   ├── ClientConnectionManager.py
│   ├── ServerConnectionManager.py
│   ├── UserClientManager.py
│   ├── UserServerManager.py
│   └── DbManager.py
├── client.py
├── server.py
└── config.py
```

## Komponenty

### Serwer
- **ServerConnectionManager** - zarządza połączeniami TCP
  - Obsługa połączeń klientów
  - Wysyłanie/odbieranie danych
  - Zarządzanie socketami

- **UserServerManager** - logika biznesowa
  - Obsługa komend użytkownika
  - Zarządzanie uprawnieniami
  - Przetwarzanie żądań

- **DbManager** - warstwa danych
  - Zapis/odczyt użytkowników
  - Zapis/odczyt wiadomości
  - Zarządzanie plikami JSON

### Klient
- **ClientConnectionManager** - komunikacja z serwerem
  - Nawiązywanie połączenia
  - Wysyłanie komend
  - Odbieranie odpowiedzi

- **UserClientManager** - interfejs użytkownika
  - Obsługa komend:
    - send_message - wysyłanie wiadomości
    - read_message - czytanie wiadomości
    - read_new_message - czytanie nowych
    - read_message_from_user - wiadomości od użytkownika
    - read_all_message - wszystkie wiadomości
    - login/logout - zarządzanie sesją

### Model
- **User** - model użytkownika
  - Dane użytkownika
  - Uprawnienia
  - Zarządzanie rolami

## Dostępne Komendy
- **send** - wysyłanie wiadomości
- **read** - czytanie nowych wiadomości
- **read-u** - wiadomości od użytkownika
- **read-a** - wszystkie wiadomości
- **read-o** - wiadomości innych (admin)
- **login** - logowanie
- **logout** - wylogowanie
- **help** - lista komend
- **info** - info o użytkowniku (admin)
- **create** - tworzenie użytkownika
- **delete** - usuwanie (admin)
- **edit** - edycja (admin)

## Uprawnienia
### Rola: admin
- send: ✓
- read: ✓
- read-u: ✓
- read-a: ✓
- read-o: ✓
- login: ✓
- logout: ✓
- help: ✓
- info: ✓
- create: ✓
- delete: ✓
- edit: ✓

### Rola: user  
- send: ✓
- read: ✓
- read-u: ✓
- read-a: ✓
- read-o: ✗
- login: ✓
- logout: ✓
- help: ✓
- info: ✗
- create: ✓
- delete: ✗
- edit: ✗
