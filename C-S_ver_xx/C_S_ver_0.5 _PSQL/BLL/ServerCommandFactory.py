import bcrypt
from datetime import datetime
from config import *
from Models.user import User
from Models.message import Message
from BLL.DatabaseRepository import DatabaseRepository
from BLL.CommandFactory import CommandFactory
from Models.MessageProtocol import ResponseDTO, MessageProtocol
import time
import secrets
import os

# Dedykowane wyjątki dla lepszej obsługi błędów
class PermissionError(Exception):
    """Wyjątek dla braku uprawnień"""
    pass

class ValidationError(Exception):
    """Wyjątek dla błędów walidacji"""
    pass

class BusinessLogicError(Exception):
    """Wyjątek dla błędów logiki biznesowej"""
    pass

class ServerCommandFactory(CommandFactory):
    """Manager dla strony serwera - wykonuje operacje biznesowe"""
    
    def __init__(self):
        super().__init__()
        self.current_user = User()
        self.database_repository = DatabaseRepository()
        self.new_messages = Message()

    def handle_send_message(self, command, receiver=None, text=None, **kwargs):
        # Sprawdź uprawnienia
        if not (self.current_user.is_user_allowed_to_command(str(command)) and self.current_user.is_logged):
            raise PermissionError("Nie masz uprawnień do tej komendy - musisz być zalogowany")
        
        # Walidacja parametrów
        if not receiver or not text:
            raise ValidationError("Odbiorca i treść wiadomości są wymagane")
        
        # Sprawdź czy odbiorca istnieje
        if not self.database_repository.is_user_in_db(receiver):
            raise BusinessLogicError(f"Użytkownik {receiver} nie istnieje")
        
        # Sprawdź limity
        number_new_message = self.database_repository.get_number_new_message_user(receiver)
        if number_new_message >= MAX_NEW_MESSAGE_STORAGE:
            raise BusinessLogicError(f"Skrzynka użytkownika {receiver} jest przepełniona")
        
        if len(text) > MAX_MESSAGE_LENGTH:
            raise ValidationError(f"Wiadomość jest za długa (max {MAX_MESSAGE_LENGTH} znaków)")
        
        # Wykonaj operację
        self.new_messages.id = self._generate_id()
        self.new_messages.username = receiver
        self.new_messages.sender = self.current_user.username
        self.new_messages.text = self._validate_string(text)
        self.new_messages.send_time = datetime.now().strftime('%Y-%m-%d godz. %H:%M')
        self.new_messages.read_time = None
        self.new_messages.is_read = 0
        
        self.database_repository.add_message_into_db(self.new_messages)
        
        return {
            "message": f"Wiadomość do {receiver} została wysłana",
            "message_id": self.new_messages.id,
            "receiver": receiver,
            "send_time": self.new_messages.send_time
        }

    def handle_read_new_message(self, command, **kwargs):
        # Sprawdź uprawnienia
        if not (self.current_user.is_user_allowed_to_command(str(command)) and self.current_user.is_logged):
            raise PermissionError("Nie masz uprawnień do tej komendy - musisz być zalogowany")
        
        # Pobierz nowe wiadomości
        new_messages = self.database_repository.get_all_new_messages_user(self.current_user.username)
        self.database_repository.change_message_status_into_read(self.current_user.username)
        
        if new_messages:
            formatted_messages = []
            for message in new_messages:
                formatted_messages.append({
                    "text": message[0],
                    "sender": message[1],
                    "send_time": message[2],
                    "formatted": f"Wiadomość od: {message[1]}: {message[0]} / wysłano: {message[2]}"
                })
            
            return {
                "messages": formatted_messages,
                "count": len(formatted_messages),
                "status": "mark_as_read"
            }
        else:
            return {
                "messages": [],
                "count": 0,
                "status": "no_new_messages"
            }

    def handle_read_message_current_user_from_sender(self, command, sender=None, **kwargs):
        if self.current_user.is_user_allowed_to_command(str(command)) and self.current_user.is_logged:
            return self.database_repository.get_all_messages_user_from_sender(self.current_user.username, sender)
        else:
            return "Nie masz uprawnień do tej komendy"

    def handle_read_all_message_current_user(self, command, **kwargs):
        if self.current_user.is_user_allowed_to_command(str(command)) and self.current_user.is_logged:
            messages = self.database_repository.get_all_messages_user(self.current_user.username)
            self.database_repository.change_message_status_into_read(self.current_user.username)
            return messages
        else:
            return "Nie masz uprawnień do tej komendy"

    def handle_read_message_user_from_sender(self, command, username=None, sender=None, **kwargs):
        if self.current_user.is_user_allowed_to_command(str(command)) and self.current_user.is_logged:
            messages = self.database_repository.get_all_messages_user_from_sender(username, sender)
            self.database_repository.change_message_status_into_read(self.current_user.username)
            return messages
        else:
            return "Nie masz uprawnień do tej komendy"

    def handle_login(self, command, username=None, password=None, **kwargs):
        # Walidacja parametrów
        if not username or not password:
            raise ValidationError("Nazwa użytkownika i hasło nie mogą być puste")
        
        # Sprawdź uprawnienia
        if not (self.current_user.is_user_allowed_to_command(str(command)) and not self.current_user.is_logged):
            raise PermissionError("Nie masz uprawnień do tej komendy lub jesteś już zalogowany")
        
        try:
            # Pobierz dane użytkownika z bazy
            stored_password = self.database_repository.get_user_password(username)
            stored_role = self.database_repository.get_user_role(username)
            
            # Sprawdź hasło
            if not stored_password or not bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                raise BusinessLogicError("Nieprawidłowa nazwa użytkownika lub hasło")
            
            # Zaloguj użytkownika
            self.database_repository.change_login_time_in_db(username)
            self.current_user.username = username
            self.current_user.password = stored_password
            self.current_user.is_logged = True
            self.current_user.role = stored_role
            
            return {
                "message": "Użytkownik został zalogowany",
                "username": username,
                "role": stored_role,
                "login_time": datetime.now().isoformat()
            }
            
        except UnicodeEncodeError:
            raise ValidationError("Hasło zawiera nieprawidłowe znaki")

    def handle_logout(self, command, **kwargs):
        # Sprawdź uprawnienia
        if not (self.current_user.is_user_allowed_to_command(str(command)) and self.current_user.is_logged):
            raise PermissionError("Użytkownik nie był zalogowany lub nie ma uprawnień")
        
        # Wyloguj użytkownika
        username = self.current_user.username
        self.current_user.is_logged = False
        
        return {
            "message": "Użytkownik został wylogowany",
            "username": username,
            "logout_time": datetime.now().isoformat()
        }

    def handle_get_help(self, command, **kwargs):
        # Sprawdź uprawnienia (help dostępny dla wszystkich)
        if not self.current_user.is_user_allowed_to_command(str(command)):
            raise PermissionError("Nie masz uprawnień do tej komendy")
        
        # Przygotuj listę pomocy
        help_commands = []
        for key, value in DIC_HELP.items():
            help_commands.append({
                "command": key,
                "description": value
            })
        
        return {
            "commands": help_commands,
            "count": len(help_commands)
        }

    def handle_get_user_info(self, command, username=None, **kwargs):
        if self.current_user.is_user_allowed_to_command(str(command)) and self.current_user.is_logged:
            return self.database_repository.get_user_info(username)
        else:
            return "Nie masz uprawnień do tej komendy"

    def handle_create_new_user(self, command, username=None, password=None, **kwargs):
        if self.current_user.is_user_allowed_to_command(str(command)) and not self.current_user.is_logged:
            if self.database_repository.is_user_in_db(username):
                return "Użytkownik już istnieje"
            elif len(password) < MIN_PASSWORD_LENGTH or len(username) < MIN_USERNAME_LENGTH:
                return f"Hasło i nazwa użytkownika muszą mieć minimum {MIN_PASSWORD_LENGTH} znaki"
            else:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                user = {
                    "id": self._generate_id(),
                    "username": username,
                    "role": "user",
                    "password": hashed_password.decode('utf-8'),
                    "login_time": None,
                    "create_time": datetime.now().isoformat()
                }
                
                is_add = self.database_repository.add_user_into_db(user)
                if is_add:
                    return "Użytkownik został dodany do bazy danych"
                else:
                    return "Użytkownik nie został dodany do bazy danych"
        else:
            return "Nie masz uprawnień do tej komendy lub jesteś już zalogowany"

    def handle_delete_user(self, command, username=None, **kwargs):
        if (self.current_user.is_user_allowed_to_command(str(command)) and 
            self.current_user.is_logged and username != self.current_user.username):
            
            is_delete = self.database_repository.delete_user_from_db(username)
            if is_delete:
                return "Użytkownik został usunięty"
            else:
                return "Użytkownik nie został usunięty"
        else:
            return "Nie masz uprawnień do tej komendy"

    def handle_edit_user_role(self, command, username=None, new_role=None, **kwargs):
        is_user_in_db = self.database_repository.is_user_in_db(username)
        if (self.current_user.is_user_allowed_to_command(command) and 
            self.current_user.is_logged and is_user_in_db):
            
            self.database_repository.edit_user_role_in_db(username, new_role)
            return "Rola została zmieniona"
        else:
            return "Nie masz uprawnień do tej komendy lub użytkownik nie istnieje"

    def _handle_unknown_command(self, command):
        return f"Nieznana komenda: {command}"
    
    def _generate_id(self):
        """Generuje unikalny numeryczny ID (timestamp + losowe bity)"""
        timestamp_ms = int(time.time() * 1000)
        random_bits = secrets.randbits(ID_RANDOM_BITS)  # Configurable bits of randomness
        return (timestamp_ms << ID_RANDOM_BITS) | random_bits
    
    def process_request(self, request_dto):
        """Przetwarza żądanie DTO i zwraca odpowiedź DTO"""
        try:
            command = request_dto.command
            data = request_dto.data
            
            if not self.is_valid_command(command):
                return MessageProtocol.create_error_response(
                    f"Nieznana komenda: {command}", 
                    "UNKNOWN_COMMAND"
                )
            
            # Wykonaj komendę - może rzucić wyjątek
            result = self.command_map[command](command, **data)
            
            # Zwróć pozytywną odpowiedź z danymi
            if isinstance(result, str):
                # Jeśli result jest stringiem, użyj go jako message
                return MessageProtocol.create_success_response(result)
            elif isinstance(result, dict):
                # Jeśli result jest słownikiem, użyj message z niego lub domyślny
                message = result.get('message', 'Operacja wykonana pomyślnie')
                return MessageProtocol.create_success_response(message, result)
            else:
                # Inne typy danych
                return MessageProtocol.create_success_response(
                    "Operacja wykonana pomyślnie", 
                    {"data": result}
                )
            
        except PermissionError as e:
            return MessageProtocol.create_error_response(
                str(e),
                "PERMISSION_ERROR"
            )
        except ValidationError as e:
            return MessageProtocol.create_error_response(
                str(e),
                "VALIDATION_ERROR"
            )
        except BusinessLogicError as e:
            return MessageProtocol.create_error_response(
                str(e),
                "BUSINESS_LOGIC_ERROR"
            )
        except Exception as e:
            return MessageProtocol.create_error_response(
                f"Nieoczekiwany błąd: {str(e)}",
                "PROCESSING_ERROR"
            )
