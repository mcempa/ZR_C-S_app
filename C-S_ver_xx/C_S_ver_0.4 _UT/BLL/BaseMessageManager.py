import bcrypt
from datetime import datetime
from config import *
from Models.user import User
from BLL.DbManager import DbManager
import time
from abc import ABC, abstractmethod

class BaseMessageManager(ABC):
    """Bazowa klasa z wspólną logiką dla serwera i klienta"""
    
    def __init__(self):
        self.command_map = {
            "send": self.handle_send_message,
            "read": self.handle_read_new_message,
            "read-u": self.handle_read_message_current_user_from_sender,
            "read-a": self.handle_read_all_message_current_user,
            "read-o": self.handle_read_message_user_from_sender,
            "login": self.handle_login,
            "logout": self.handle_logout,
            "help": self.handle_get_help,
            "info": self.handle_get_user_info,
            "create": self.handle_create_new_user,
            "delete": self.handle_delete_user,
            "edit": self.handle_edit_user_role,
        }

    def process_command(self, command, *args, **kwargs):
        """Uniwersalna metoda przetwarzania komend"""
        if command in self.command_map:
            return self.command_map[command](command, *args, **kwargs)
        else:
            return self._handle_unknown_command(command)

    def _validate_string(self, text):
        """Walidacja i sanityzacja tekstu"""
        if not isinstance(text, str):
            try:
                text = str(text)
            except Exception as e:
                raise ValueError(f"Nie można przekonwertować wartości na tekst: {e}")
        
        forbidden_chars = FORBIDDEN_CHARS
        safe_text = text
        for char in forbidden_chars:
            safe_text = safe_text.replace(char, '')
            
        return safe_text.strip()

    

    # Abstract methods - muszą być zaimplementowane w klasach pochodnych
    @abstractmethod
    def handle_send_message(self, command, **kwargs):
        pass

    @abstractmethod
    def handle_read_new_message(self, command, **kwargs):
        pass

    @abstractmethod
    def handle_read_message_current_user_from_sender(self, command, **kwargs):
        pass

    @abstractmethod
    def handle_read_all_message_current_user(self, command, **kwargs):
        pass

    @abstractmethod
    def handle_read_message_user_from_sender(self, command, **kwargs):
        pass

    @abstractmethod
    def handle_login(self, command, **kwargs):
        pass

    @abstractmethod
    def handle_logout(self, command, **kwargs):
        pass

    @abstractmethod
    def handle_get_help(self, command, **kwargs):
        pass

    @abstractmethod
    def handle_get_user_info(self, command, **kwargs):
        pass

    @abstractmethod
    def handle_create_new_user(self, command, **kwargs):
        pass

    @abstractmethod
    def handle_delete_user(self, command, **kwargs):
        pass

    @abstractmethod
    def handle_edit_user_role(self, command, **kwargs):
        pass

    @abstractmethod
    def _handle_unknown_command(self, command):
        pass