import bcrypt
from datetime import datetime
from config import *
from Models.user import User
from Models.message import Message
from BLL.DbManager import DbManager
from BLL.BaseMessageManager import BaseMessageManager
import time
import secrets
import os

class ServerMessageManager(BaseMessageManager):
    """Manager dla strony serwera - wykonuje operacje biznesowe"""
    
    def __init__(self):
        super().__init__()
        self.current_user = User()
        self.db_manager = DbManager()
        self.new_messages = Message()

    def handle_send_message(self, command, receiver=None, text=None, **kwargs):
        number_new_message = self.db_manager.get_number_new_message_user(receiver)
        is_receiver_in_db = self.db_manager.is_user_in_db(receiver)
        
        if (self.current_user.is_user_allowed_to_command(str(command)) and 
            self.current_user.is_logged and is_receiver_in_db):
            
            if number_new_message < MAX_NEW_MESSAGE_STORAGE and len(text) <= MAX_MESSAGE_LENGTH:
                
                # Przypisz ID przed zapisem
                self.new_messages.id = self._generate_id()
                self.new_messages.username = receiver
                self.new_messages.sender = self.current_user.username
                self.new_messages.text = self._validate_string(text)
                self.new_messages.send_time = datetime.now().strftime('%Y-%m-%d godz. %H:%M')
                self.new_messages.read_time = None
                self.new_messages.is_read = 0
                
                self.db_manager.add_message_into_db(self.new_messages)
                return f"Wiadomość do {receiver} została wysłana"
            else:
                return f"Nie możesz wysłać wiadomości do {receiver} - jego skrzynka jest przepełniona lub wiadomość jest dłuższa niż 255 znaków"
        else:
            return f"Nie masz uprawnień do tej komendy lub użytkownik {receiver} nie istnieje"

    def handle_read_new_message(self, command, **kwargs):
        if self.current_user.is_user_allowed_to_command(str(command)) and self.current_user.is_logged:
            new_messages = self.db_manager.get_all_new_messages_user(self.current_user.username)
            self.db_manager.change_message_status_into_read(self.current_user.username)
            
            if new_messages:
                response = []
                for message in new_messages:
                    response.append(f"Wiadomosc od: {message[1]}: {message[0]} / wysłano: {message[2]}")
                return "\n".join(response)
            else:
                return "Nie masz nowych wiadomości"
        else:
            return "Nie masz uprawnień do tej komendy"

    def handle_read_message_current_user_from_sender(self, command, sender=None, **kwargs):
        if self.current_user.is_user_allowed_to_command(str(command)) and self.current_user.is_logged:
            return self.db_manager.get_all_messages_user_from_sender(self.current_user.username, sender)
        else:
            return "Nie masz uprawnień do tej komendy"

    def handle_read_all_message_current_user(self, command, **kwargs):
        if self.current_user.is_user_allowed_to_command(str(command)) and self.current_user.is_logged:
            messages = self.db_manager.get_all_messages_user(self.current_user.username)
            self.db_manager.change_message_status_into_read(self.current_user.username)
            return messages
        else:
            return "Nie masz uprawnień do tej komendy"

    def handle_read_message_user_from_sender(self, command, username=None, sender=None, **kwargs):
        if self.current_user.is_user_allowed_to_command(str(command)) and self.current_user.is_logged:
            messages = self.db_manager.get_all_messages_user_from_sender(username, sender)
            self.db_manager.change_message_status_into_read(self.current_user.username)
            return messages
        else:
            return "Nie masz uprawnień do tej komendy"

    def handle_login(self, command, username=None, password=None, **kwargs):
        try:
            if not username or not password:
                return "Nazwa użytkownika i hasło nie mogą być puste"
                
            if self.current_user.is_user_allowed_to_command(str(command)) and not self.current_user.is_logged:
                stored_password = self.db_manager.get_user_password(username)
                stored_role = self.db_manager.get_user_role(username)
                
                if stored_password and bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    self.db_manager.change_login_time_in_db(username)
                    self.current_user.username = username
                    self.current_user.password = stored_password
                    self.current_user.is_logged = True
                    self.current_user.role = stored_role
                    return "Użytkownik został zalogowany"
                else:
                    return "Nieprawidłowa nazwa użytkownika lub hasło"
            else:
                return "Nie masz uprawnień do tej komendy lub jesteś już zalogowany"
                
        except UnicodeEncodeError:
            return "Hasło zawiera nieprawidłowe znaki"
        except Exception as e:
            return f"Wystąpił nieoczekiwany błąd: {str(e)}"

    def handle_logout(self, command, **kwargs):
        if self.current_user.is_user_allowed_to_command(str(command)) and self.current_user.is_logged:
            self.current_user.is_logged = False
            return "Użytkownik został wylogowany"
        return "Użytkownik nie był zalogowany"

    def handle_get_help(self, command, **kwargs):
        if self.current_user.is_user_allowed_to_command(str(command)):
            help_list = []
            for key, value in DIC_HELP.items():
                help_list.append(f"{key}: {value}")
            return "\n".join(help_list)
        else:
            return "Nie masz uprawnień do tej komendy"

    def handle_get_user_info(self, command, username=None, **kwargs):
        if self.current_user.is_user_allowed_to_command(str(command)) and self.current_user.is_logged:
            return self.db_manager.get_user_info(username)
        else:
            return "Nie masz uprawnień do tej komendy"

    def handle_create_new_user(self, command, username=None, password=None, **kwargs):
        if self.current_user.is_user_allowed_to_command(str(command)) and not self.current_user.is_logged:
            if self.db_manager.is_user_in_db(username):
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
                
                is_add = self.db_manager.add_user_into_db(user)
                if is_add:
                    return "Użytkownik został dodany do bazy danych"
                else:
                    return "Użytkownik nie został dodany do bazy danych"
        else:
            return "Nie masz uprawnień do tej komendy lub jesteś już zalogowany"

    def handle_delete_user(self, command, username=None, **kwargs):
        if (self.current_user.is_user_allowed_to_command(str(command)) and 
            self.current_user.is_logged and username != self.current_user.username):
            
            is_delete = self.db_manager.delete_user_from_db(username)
            if is_delete:
                return "Użytkownik został usunięty"
            else:
                return "Użytkownik nie został usunięty"
        else:
            return "Nie masz uprawnień do tej komendy"

    def handle_edit_user_role(self, command, username=None, new_role=None, **kwargs):
        is_user_in_db = self.db_manager.is_user_in_db(username)
        if (self.current_user.is_user_allowed_to_command(command) and 
            self.current_user.is_logged and is_user_in_db):
            
            self.db_manager.edit_user_role_in_db(username, new_role)
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
