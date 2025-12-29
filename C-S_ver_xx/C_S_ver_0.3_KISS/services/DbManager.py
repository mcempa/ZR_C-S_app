
from datetime import datetime
import json
from config import *


class DbManager():
    def __init__(self):
        self.users_db = PATH_USERS_DB
        self.messages_db = PATH_MESSAGES_DB

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

    @handle_db_exceptions
    def add_message_into_db(self, message):
        with open(self.messages_db, "r", encoding="utf-8") as file:
            data = json.load(file)
        data["messages"].append(message)

        with open(self.messages_db, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return True

    @handle_db_exceptions
    def delete_message_from_db(self, message_id, username):
        with open(self.messages_db, "r", encoding="utf-8") as file:
            data = json.load(file)
        data["messages"] = [msg for msg in data["messages"] if msg["id"] != message_id and msg["username"] != username]
        with open(self.messages_db, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return True
 
    @handle_db_exceptions
    def get_all_messages_user(self, username):
        with open(self.messages_db, "r", encoding="utf-8") as file:
            data = json.load(file)
        filtered_messages = [msg["text"] for msg in data["messages"] if msg["username"] == username]
        return filtered_messages
      
    @handle_db_exceptions
    def get_all_messages_user_from_sender(self, username, sender):
            with open(self.messages_db, "r", encoding="utf-8") as file:
                data = json.load(file)
            filtered_messages = [msg["text"] for msg in data["messages"] if (msg["username"] == username and msg["sender"] == sender)]
            return filtered_messages
        
    @handle_db_exceptions
    def get_all_new_messages_user(self, username):
        with open(self.messages_db, "r", encoding="utf-8") as file:
            #print("test)")
            data = json.load(file)
        new_messages = list([msg["text"], msg["sender"], msg["send_time"]] for msg in data["messages"] if (msg["username"] == username and msg["is_read"] == 0))
        return new_messages
             
    @handle_db_exceptions
    def get_number_new_message_user(self, username):
        with open(self.messages_db, "r", encoding="utf-8") as file:
            data = json.load(file)
        new_messages = [msg for msg in data["messages"] if (msg["username"] == username and msg["is_read"] == 0)]
        return len(new_messages)
    
    @handle_db_exceptions
    def change_message_status_into_read(self, username):
        with open(self.messages_db, "r", encoding="utf-8") as file:
            data = json.load(file)
        for msg in data["messages"]:
            if msg["username"] == username and msg["is_read"] == 0:
                msg["is_read"] = 1
                msg["read_time"] = datetime.now().strftime("%Y-%m-%d godz. %H:%M")
        with open(self.messages_db, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)    
        return True
            
    @handle_db_exceptions           
    def get_user_info(self, username):
        with open(self.users_db, "r", encoding="utf-8") as file:
            data = json.load(file)
        for user in data["users"]:
                if user["username"] == username:
                    user_info = user
                    break
        return user_info
    
    @handle_db_exceptions
    def delete_user_from_db(self, username):  #usuwanie po nazwa uzytkownika, zalozono ze jest unikalna
        with open(self.users_db, "r", encoding="utf-8") as file:
            data = json.load(file)
        data["users"] = [user for user in data["users"] if user["username"] != username] #nowa lista użytkowników bez usuniętego
        with open(self.users_db, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return True
    
    #@handle_db_exceptions            
    def add_user_into_db(self, user):
        with open(self.users_db, "r", encoding="utf-8") as file:
            data = json.load(file)
        data["users"].append(user) 
        with open(self.users_db, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return True

    @handle_db_exceptions
    def edit_user_role_in_db(self, username, new_role):
        with open(self.users_db, "r", encoding="utf-8") as file:
            data = json.load(file)
        #print(users)
        for user in data["users"]:
            if user["username"] == username :
                user["role"] = new_role
                print(f"Zmieniono rolę użytkownika {username} na {new_role}")
                break
        # Zapisz zaktualizowane dane
        with open(self.users_db, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)    
        return True
    
    @handle_db_exceptions
    def change_login_time_in_db(self, username):
        with open(self.users_db, "r", encoding="utf-8") as file:
            data = json.load(file)
        print(username)
        for user in data["users"]:
            if user["username"] == username :
                user["login_time"] = datetime.now().isoformat()
                break
        # Zapisz zaktualizowane dane
        with open(self.users_db, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)    
        return True
    
    @handle_db_exceptions
    def is_user_in_db(self, username):
        with open(self.users_db, "r", encoding="utf-8") as file:
            data = json.load(file)
        #print(data)
        users = data.get("users", {})
        return any(
            user.get("username") == str(username)
            for user in users
        )
    
    @handle_db_exceptions
    def is_message_in_db(self, message_id):
        with open(self.messages_db, "r", encoding="utf-8") as file:
            data = json.load(file)
        #print(data)
        messages = data.get("messages", {})
        return any(
            message.get("id") == str(message_id)
            for message in messages
        )
    
    @handle_db_exceptions
    def is_user_password_in_db(self, username, password):
        with open(self.users_db, "r", encoding="utf-8") as file:
            data = json.load(file)
        #print(data)
        users = data.get("users", {})
        return any(
            user.get("username") == str(username) and 
            user.get("password") == str(password)
            for user in users
        )
    
    @handle_db_exceptions
    def get_user_password(self, username):
        with open(PATH_USERS_DB, "r", encoding="utf-8") as file:
            data = json.load(file)
        password = None
        for user in data["users"]:
                if user["username"] == username:
                    password = user["password"]
                    break
        return password
    
    @handle_db_exceptions
    def get_user_role(self, username):
        with open(PATH_USERS_DB, "r", encoding="utf-8") as file:
            data = json.load(file)
        role = None
        for user in data["users"]:
                if user["username"] == username:
                    role = user["role"]
                    break
        return role
           


    