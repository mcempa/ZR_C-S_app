
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

PATH_USERS_DB = "data/users.json"
PATH_MESSAGES_DB = "data/messages.json"

MAX_MESSAGE_LENGTH = 255
MAX_NEW_MESSAGE_STORAGE = 5
