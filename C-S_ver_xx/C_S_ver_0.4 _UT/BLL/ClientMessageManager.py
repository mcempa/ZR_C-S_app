from BLL.BaseMessageManager import BaseMessageManager

class ClientMessageManager(BaseMessageManager):
    """Manager dla strony klienta - tworzy żądania do wysłania na serwer"""
    
    def __init__(self):
        super().__init__()

    def _create_request(self, command, data_dict):
        """Tworzy podstawowy format żądania dla serwera"""
        return [str(command), data_dict]

    def handle_send_message(self, command, receiver=None, text=None, **kwargs):
        return self._create_request(command, {
            "receiver": receiver,
            "text": text
        })

    def handle_read_new_message(self, command, **kwargs):
        return self._create_request(command, {})

    def handle_read_message_current_user_from_sender(self, command, sender=None, **kwargs):
        return self._create_request(command, {
            "sender": sender
        })

    def handle_read_all_message_current_user(self, command, **kwargs):
        return self._create_request(command, {})

    def handle_read_message_user_from_sender(self, command, username=None, sender=None, **kwargs):
        return self._create_request(command, {
            "username": username,
            "sender": sender
        })

    def handle_login(self, command, username=None, password=None, **kwargs):
        return self._create_request(command, {
            "username": username,
            "password": password
        })

    def handle_logout(self, command, **kwargs):
        return self._create_request(command, {})

    def handle_get_help(self, command, **kwargs):
        return self._create_request(command, {})

    def handle_get_user_info(self, command, username=None, **kwargs):
        return self._create_request(command, {
            "username": username
        })

    def handle_create_new_user(self, command, username=None, password=None, **kwargs):
        return self._create_request(command, {
            "username": username,
            "password": password
        })

    def handle_delete_user(self, command, username=None, **kwargs):
        return self._create_request(command, {
            "username": username
        })

    def handle_edit_user_role(self, command, username=None, new_role=None, **kwargs):
        return self._create_request(command, {
            "username": username,
            "new_role": new_role
        })

    def _handle_unknown_command(self, command):
        return ["error", {"message": f"Nieznana komenda: {command}"}]

    # ============= INTERACTIVE INPUT METHODS =============

    def prepare_request_interactive(self):
        """Interaktywne przygotowanie żądania z inputem użytkownika"""
        input_handlers = {
            "help": lambda: {},
            "read-a": lambda: {},
            "read": lambda: {},
            "logout": lambda: {},
            "login": self._get_login_input,
            "create": self._get_create_input,
            "send": self._get_send_message_input,
            "read-u": self._get_sender_input,
            "read-o": self._get_read_message_input,
            "edit": self._get_edit_role_input,
            "info": self._get_username_input,
            "delete": self._get_username_input,
        }

        command = input("Podaj komendę: ").lower().strip()
        
        if command not in self.command_map:
            print("Komenda nie istnieje")
            return command, {}

        data_input = input_handlers.get(command, lambda: {})()
        return command, data_input

    def _get_login_input(self):
        username = input("Podaj nazwę użytkownika: ").strip().lower()
        password = input("Podaj hasło użytkownika: ")
        return {"username": username, "password": password}

    def _get_create_input(self):
        username = input("Podaj nazwę użytkownika: ").strip().lower()
        password = input("Podaj hasło użytkownika: ")
        return {"username": username, "password": password}

    def _get_send_message_input(self):
        receiver = input("Odbiorca wiadomości - podaj nazwę użytkownika: ").strip().lower()
        text = input("Wpisz treść wiadomości: ")
        return {"receiver": receiver, "text": text}

    def _get_sender_input(self):
        sender = input("Podaj nazwę użytkownika, od którego wiadomości chcesz przeglądać: ").strip().lower()
        return {"sender": sender}

    def _get_read_message_input(self):
        username = input("Podaj nazwę użytkownika, którego wiadomości chcesz przeglądać: ").strip().lower()
        sender = input("Podaj nazwę nadawcy wiadomości: ").strip().lower()
        return {"username": username, "sender": sender}

    def _get_edit_role_input(self):
        username = input("Podaj nazwę użytkownika, którego rolę chcesz zmienić: ").strip().lower()
        new_role = input("Nowa rola: ").strip().lower()
        return {"username": username, "new_role": new_role}

    def _get_username_input(self):
        username = input("Podaj nazwę użytkownika: ").strip().lower()
        return {"username": username}