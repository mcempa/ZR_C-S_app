
SERVER_CONFIG = {
    "host": "127.0.0.1",
    "port":  64623,
    "max_connections": 5,
    "buffer_size": 1024
}

ROLE_PERMISSIONS = {
        'admin': {
            "send"   : True,
            "read"   : True,
            "read-u" : True,
            "read-a" : True,
            "read-o" : True,
            "login"  : True,
            "logout" : True,
            "help"   : True,
            "info"   : True,
            "create" : True,
            "delete" : True,
            "edit"   : True
                },
            
        'user': {
            "send"   : True,
            "read"   : True,
            "read-u" : True,
            "read-a" : True,
            "read-o" : False,
            "login"  : True,
            "logout" : True,
            "help"   : True,
            "info"   : False,
            "create" : True,
            "delete" : False,
            "edit"   : False
            }
            }

DIC_HELP = {
        "send"   : "send - wysyłanie wiadomości do innego zarejestrowanego użytkownika",
        "read"   : "read - czytanie nowych wiadomości",
        "read-u" : "read-u - przegląd wszystkich wiadomości od wybranego użytkownika",
        "read-a" : "read-a - przegląd wszystkich wiadomości jakie ma użytkownik",
        "read-o" : "read-o - przegląd wszystkich wiadomości innego użytkownika (tylko  admin)",
        "login"  : "login - logowanie do systemu",
        "logout" : "logout - wylogowanie z systemu",
        "help"   : "help - zwraca listę dostępnych komend z krótkim opisem",
        "info"   : "info - zwraca informacje o wybranym użytkowniku (tylko admin)",
        "create" : "create - tworzenie nowego użytkownika",
        "delete" : "delete - usuwanie użytkownika (tylko admin)",
        "edit"   : "edit - edycja roli użytkownika  (tylko admin)"
        }

# Database configuration
DATABASE_TYPE = "POSTGRESQL"  # "JSON", "SQL", "POSTGRESQL", "MONGO" - easy switch between database types

# JSON Database paths
PATH_USERS_DB = "Database/users.json"
PATH_MESSAGES_DB = "Database/messages.json"

# SQL Database configuration (for future use)
SQL_CONNECTION_STRING = "sqlite:///database.db"

# PostgreSQL Database configuration
POSTGRESQL_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "client_server_db",
    "username": "app_user",
    "password": "app_password"
}

# Validation constants
MIN_USERNAME_LENGTH = 2
MIN_PASSWORD_LENGTH = 2
MAX_MESSAGE_LENGTH = 255
MAX_NEW_MESSAGE_STORAGE = 5
MAX_REQUEST_SIZE = 2048
MAX_COMMAND_LENGTH = 50
MAX_USERNAME_LENGTH = 50
MAX_PASSWORD_LENGTH = 100

# ID generation constants
ID_RANDOM_BITS = 20  # bits of randomness for ID generation
ID_HEX_BYTES = 4     # bytes for hex ID generation

# Connection retry settings
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 1.0
CONNECTION_TIMEOUT = 300.0  # 5 minut zamiast 5 sekund

FORBIDDEN_CHARS = ['"', "'", ';', '{', '}', '[', ']']