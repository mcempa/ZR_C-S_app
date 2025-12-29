from datetime import datetime
import json
from config import *
from BLL.RepositoryFactory import RepositoryFactory


class DbManager():
    def __init__(self):
        # Factory pattern - decyzja o bazie danych w konfiguracji
        self.users_repository = RepositoryFactory.create_users_repository()
        self.messages_repository = RepositoryFactory.create_messages_repository()

    @staticmethod
    def handle_db_exceptions(func):           
        def wrapper(self, *args, **kwargs):   # wrapper to nowa funkcja, która "owija" oryginalną
            try:
                return func(self, *args, **kwargs)  # wywołanie oryginalnej funkcji
            except FileNotFoundError:
                print(f"Nie znaleziono pliku bazy")
                return False
            except json.JSONDecodeError:
                print("Błąd podczas parsowania pliku JSON")
                return False
            except PermissionError:
                print(f"Brak uprawnień do zapisu pliku")
                return False
            except IOError as e:
                print(f"Błąd podczas operacji na pliku: {e}")
                return False
            except ValueError as e:
                print(f"Błąd walidacji danych: {e}")
                return False
            except Exception as e:
                print(f"Wystąpił nieoczekiwany błąd: {e}")
                return False
        return wrapper   
    
    def _sanitize_string(self, text):
        """Sanityzacja tekstu - usunięcie niebezpiecznych znaków"""
        if not isinstance(text, str):
            try:
                text = str(text)
            except Exception as e:
                raise ValueError(f"Nie można przekonwertować wartości na tekst: {e}")
        
        # Usunięcie niebezpiecznych znaków
        for char in FORBIDDEN_CHARS:
            text = text.replace(char, '')
            
        return text.strip()

    @handle_db_exceptions
    def add_message_into_db(self, message_data):
        # Walidacja danych wiadomości
        if not hasattr(message_data, 'username') or not hasattr(message_data, 'text'):
            raise ValueError("Dane wiadomości są niepełne")
        
        # Walidacja długości
        if len(message_data.text) > MAX_MESSAGE_LENGTH:
            raise ValueError(f"Wiadomość przekracza maksymalną długość {MAX_MESSAGE_LENGTH}")
        if len(message_data.username) > MAX_USERNAME_LENGTH:
            raise ValueError(f"Nazwa użytkownika przekracza maksymalną długość {MAX_USERNAME_LENGTH}")
        
        # Sanityzacja danych
        message_data.text = self._sanitize_string(message_data.text)
        message_data.username = self._sanitize_string(message_data.username)
        message_data.sender = self._sanitize_string(message_data.sender)
        
        # Konwersja obiektu Message do słownika dla JSON
        message_dict = message_data.to_dict()
        
        return self.messages_repository.save(message_dict)

    @handle_db_exceptions
    def delete_message_from_db(self, message_id, username):
        message = self.messages_repository.find_by_id(message_id)
        if message and message.get("username") == username:
            return self.messages_repository.delete(message_id)
        return False
 
    @handle_db_exceptions
    def get_all_messages_user(self, username):
        return [msg["text"] for msg in self.messages_repository.find_by_field("username", username)]
      
    @handle_db_exceptions
    def get_all_messages_user_from_sender(self, username, sender):
        messages = self.messages_repository.find_by_field("username", username)
        return [msg["text"] for msg in messages if msg.get("sender") == sender]
        
    @handle_db_exceptions
    def get_all_new_messages_user(self, username):
        messages = self.messages_repository.find_by_field("username", username)
        return [[msg["text"], msg["sender"], msg["send_time"]] 
                for msg in messages if msg.get("is_read") == 0]
             
    @handle_db_exceptions
    def get_number_new_message_user(self, username):
        messages = self.messages_repository.find_by_field("username", username)
        return len([msg for msg in messages if msg.get("is_read") == 0])
    
    @handle_db_exceptions
    def change_message_status_into_read(self, username):
        messages = self.messages_repository.find_by_field("username", username)
        for msg in messages:
            if msg.get("is_read") == 0:
                self.messages_repository.update(msg["id"], {
                    "is_read": 1,
                    "read_time": datetime.now().strftime("%Y-%m-%d godz. %H:%M")
                })
        return True
            
    @handle_db_exceptions           
    def get_user_info(self, username):
        user = self.users_repository.find_by_field("username", username)
        if user:
            user_info = user[0].copy()
            user_info.pop("password", None)
            return user_info
        return None
    
    @handle_db_exceptions
    def delete_user_from_db(self, username):
        # Walidacja parametru username
        if not username or not isinstance(username, str):
            raise ValueError("Nazwa użytkownika jest wymagana i musi być tekstem")
        
        # Sprawdzenie czy użytkownik istnieje
        user = self.users_repository.find_by_field("username", username)
        if not user or len(user) == 0:
            raise ValueError(f"Użytkownik {username} nie istnieje w bazie danych")
        
        # Pobranie ID użytkownika
        user_id = user[0].get("id")
        if not user_id:
            raise ValueError(f"Nie znaleziono ID dla użytkownika {username}")
        
        # Usunięcie użytkownika
        result = self.users_repository.delete(user_id)
        if result:
            print(f"Użytkownik {username} został pomyślnie usunięty")
        return result
    
    @handle_db_exceptions            
    def add_user_into_db(self, user):
        # Walidacja danych użytkownika
        if not isinstance(user, dict):
            raise ValueError("Dane użytkownika muszą być słownikiem")
        
        required_fields = ["username", "password", "role"]
        for field in required_fields:
            if field not in user or not user[field]:
                raise ValueError(f"Pole {field} jest wymagane")
        
        # Walidacja długości pól
        if len(user["username"]) > MAX_USERNAME_LENGTH:
            raise ValueError(f"Nazwa użytkownika przekracza maksymalną długość {MAX_USERNAME_LENGTH}")
        if len(user["password"]) > MAX_PASSWORD_LENGTH:
            raise ValueError(f"Hasło przekracza maksymalną długość {MAX_PASSWORD_LENGTH}")
        
        # Sanityzacja danych
        user["username"] = self._sanitize_string(user["username"])
        
        return self.users_repository.save(user)

    @handle_db_exceptions
    def edit_user_role_in_db(self, username, new_role):
        user = self.users_repository.find_by_field("username", username)
        if user:
            print(f"Zmieniono rolę użytkownika {username} na {new_role}")
            return self.users_repository.update(user[0]["id"], {"role": new_role})
        return False
    
    @handle_db_exceptions
    def change_login_time_in_db(self, username):
        user = self.users_repository.find_by_field("username", username)
        if user:
            print(username)
            return self.users_repository.update(user[0]["id"], {
                "login_time": datetime.now().isoformat()
            })
        return False
    
    @handle_db_exceptions
    def is_user_in_db(self, username):
        return len(self.users_repository.find_by_field("username", username)) > 0
    
    @handle_db_exceptions
    def is_message_in_db(self, message_id):
        return self.messages_repository.find_by_id(message_id) is not None
    
    @handle_db_exceptions
    def is_user_password_in_db(self, username, password):
        users = self.users_repository.find_by_field("username", username)
        return any(
            user.get("password") == str(password)
            for user in users
        )
    
    @handle_db_exceptions
    def get_user_password(self, username):
        user = self.users_repository.find_by_field("username", username)
        return user[0]["password"] if user else None
    
    @handle_db_exceptions
    def get_user_role(self, username):
        user = self.users_repository.find_by_field("username", username)
        return user[0]["role"] if user else None
           


    