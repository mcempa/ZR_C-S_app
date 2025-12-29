"""
UI Handler for client-side user interactions
Handles all input/output operations - separated from business logic
"""
from Models.MessageProtocol import ResponseDTO
import json

class ClientUIHandler:
    """Handles all user interface operations for the client"""
    
    def get_command_input(self):
        """Get command from user"""
        return input("Podaj komendę: ").lower().strip()
    
    def get_login_input(self):
        """Get login credentials from user"""
        username = input("Podaj nazwę użytkownika: ").strip().lower()
        password = input("Podaj hasło użytkownika: ")
        return {"username": username, "password": password}
    
    def get_create_user_input(self):
        """Get new user data from user"""
        username = input("Podaj nazwę użytkownika: ").strip().lower()
        password = input("Podaj hasło użytkownika: ")
        return {"username": username, "password": password}
    
    def get_send_message_input(self):
        """Get message data from user"""
        receiver = input("Odbiorca wiadomości - podaj nazwę użytkownika: ").strip().lower()
        text = input("Wpisz treść wiadomości: ")
        return {"receiver": receiver, "text": text}
    
    def get_sender_input(self):
        """Get sender name for message filtering"""
        sender = input("Podaj nazwę użytkownika, od którego wiadomości chcesz przeglądać: ").strip().lower()
        return {"sender": sender}
    
    def get_read_message_input(self):
        """Get username and sender for reading messages"""
        username = input("Podaj nazwę użytkownika, którego wiadomości chcesz przeglądać: ").strip().lower()
        sender = input("Podaj nazwę nadawcy wiadomości: ").strip().lower()
        return {"username": username, "sender": sender}
    
    def get_edit_role_input(self):
        """Get data for role editing"""
        username = input("Podaj nazwę użytkownika, którego rolę chcesz zmienić: ").strip().lower()
        new_role = input("Nowa rola: ").strip().lower()
        return {"username": username, "new_role": new_role}
    
    def get_username_input(self):
        """Get username for various operations"""
        username = input("Podaj nazwę użytkownika: ").strip().lower()
        return {"username": username}
    
    def show_error(self, message):
        """Display error message to user"""
        print(f"Błąd: {message}")
    
    def show_info(self, message):
        """Display info message to user"""
        print(message)
    
    def show_response(self, response):
        """Display server response to user"""
        if isinstance(response, ResponseDTO):
            # Obsługa ResponseDTO
            if response.success:
                print(f"✓ Sukces: {response.message}")
                if response.data:
                    print(f"Dane: {response.data}")
            else:
                print(f"✗ Błąd: {response.message}")
                if response.error_code:
                    print(f"Kod błędu: {response.error_code}")
        elif isinstance(response, str):
            try:
                # Spróbuj sparsować jako ResponseDTO JSON
                response_dto = ResponseDTO.from_json(response)
                self.show_response(response_dto)  # Rekurencyjne wywołanie z ResponseDTO
            except (json.JSONDecodeError, KeyError):
                # Jeśli to nie ResponseDTO JSON, wyświetl jako zwykły tekst
                print(f"Odpowiedź serwera: {response}")
        else:
            print(f"Odpowiedź serwera: {response}")
    
    def get_command_parameters(self, command):
        """Get parameters for specific command"""
        input_handlers = {
            "help": lambda: {},
            "read-a": lambda: {},
            "read": lambda: {},
            "logout": lambda: {},
            "login": self.get_login_input,
            "create": self.get_create_user_input,
            "send": self.get_send_message_input,
            "read-u": self.get_sender_input,
            "read-o": self.get_read_message_input,
            "edit": self.get_edit_role_input,
            "info": self.get_username_input,
            "delete": self.get_username_input,
        }
        
        handler = input_handlers.get(command, lambda: {})
        return handler()
