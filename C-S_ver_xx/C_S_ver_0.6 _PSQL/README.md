# Dokumentacja Projektu Client-Server
Zaktualizowano: 2025-08-09

## Struktura Projektu (Architektura Warstwowa)
```
C_S_ver_0.4_UT/
├── BLL/ (Business Logic Layer)
│   ├── BaseMessageManager.py
│   ├── ClientConnectionManager.py
│   ├── ClientMessageManager.py
│   ├── DbManager.py
│   ├── RepositoryFactory.py
│   ├── ServerConnectionManager.py
│   └── ServerMessageManager.py
├── UI/ (User Interface Layer)
│   ├── client.py
│   └── server.py
├── DAL/ (Data Access Layer)
│   ├── base_repository.py
│   └── json_repository.py
├── Database/ (Data Storage)
│   ├── messages.json
│   └── users.json
├── Models/ (Domain Models)
│   ├── message.py
│   └── user.py
├── Tests/ (Unit Tests)
│   ├── test_client_connection_manager.py
│   ├── test_db_manager.py
│   ├── test_metody.py
│   ├── test_server_connaction_manager.py
│   └── test_user_message_manager.py
├── config.py
└── README.md
```

## Architektura Warstwowa

### BLL (Business Logic Layer) - Warstwa Logiki Biznesowej
- **BaseMessageManager** - bazowa klasa dla zarządzania wiadomościami
- **ClientConnectionManager** - zarządzanie połączeniami po stronie klienta
- **ClientMessageManager** - obsługa wiadomości klienta
- **ServerConnectionManager** - zarządzanie połączeniami po stronie serwera
- **ServerMessageManager** - obsługa wiadomości serwera
- **DbManager** - zarządzanie operacjami na bazie danych
- **RepositoryFactory** - fabryka repozytoriów

### DAL (Data Access Layer) - Warstwa Dostępu do Danych
- **base_repository.py** - abstrakcyjna klasa bazowa dla repozytoriów
- **json_repository.py** - implementacja repozytorium JSON

### Models - Modele Domenowe
- **User** - model użytkownika z danymi i uprawnieniami
- **Message** - model wiadomości

### UI (User Interface) - Warstwa Interfejsu Użytkownika
- **client.py** - aplikacja kliencka
- **server.py** - aplikacja serwerowa

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
