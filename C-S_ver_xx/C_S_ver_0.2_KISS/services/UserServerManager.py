import bcrypt
from datetime import datetime
from config import *
from models.user import User
from services.DbManager import DbManager
from datetime import datetime
import time
import os

class UserServerManager: 
    def __init__(self):
        self.current_user = User()
        self.db_manager = DbManager()
        self.command_map = {
            "send"   : self.send_message,
            "read"   : self.read_new_message,
            "read-u" : self.read_message_current_user_from_sender,
            "read-a" : self.read_message_current_user,
            "read-o" : self.read_message_user_from_sander,
            "login"  : self.login_user,
            "logout" : self.logout_user,
            "help"   : self.get_help,
            "info"   : self.get_user_info,
            "create" : self.create_new_user,
            "delete" : self.delete_user,
            "edit"   : self.edit_user_role
        }

    def get_help(self, command):
        if self.current_user.is_user_allowed_to_command(str(command)): 
            list =[] 
            for key, value in DIC_HELP.items():
                list.append(f"{key}: {value}")
            response = "\n".join(list)
        else:
            response = "Nie masz uprawnień do tej komendy"
        return response

    def send_message(self, command, receiver, text):
        number_new_message = self.db_manager.get_number_new_message_user(receiver)
        is_receiver_in_db = self.db_manager.is_user_in_db(receiver)
        #print(number_new_message)
        if self.current_user.is_user_allowed_to_command(str(command)) and self.current_user.is_logged and is_receiver_in_db:
            if number_new_message < 5 and len(text) <= 255:
                message = {
                    "id": self.generate_id_message(),
                    "username": receiver,
                    "sender": self.current_user.username,
                    "text": text,
                    "send_time": datetime.now().strftime('%Y-%m-%d godz. %H:%M'),
                    "read_time": None,
                    "is_read": 0
                }
                
                self.db_manager.add_message_into_db(message)
                response = f"Wiadomość do {receiver} została wysłana"
            else:
                response = f"Nie możesz wysłać wiadomości do {receiver} - jego skrzynka jest przepełniona lub wiadomość jest dłuższa niż 255 znaków"
        else:
            response = f"Nie masz uprawnień do tej komendy lub użytkownik {receiver} nie istnieje"
        return response

    def read_message_current_user_from_sender(self, command, sender):
        if self.current_user.is_user_allowed_to_command(str(command)) and  self.current_user.is_logged:
            messages = self.db_manager.get_all_messages_user_from_sender(self.current_user.username, sender)
            return messages 
        else:
            return "Nie masz uprawnień do tej komendy"

    def read_message_current_user(self, command):
        if self.current_user.is_user_allowed_to_command(str(command)) and  self.current_user.is_logged:
            messages = self.db_manager.get_all_messages_user(self.current_user.username)
            self.db_manager.change_message_status_into_read(self.current_user.username)
            response = messages   
        else:
            response = f"Nie masz uprawnień do tej komendy"
        return response    

    def read_message_user_from_sander(self, command, user, sender):
        if self.current_user.is_user_allowed_to_command(str(command)) and  self.current_user.is_logged:
            messages = self.db_manager.get_all_messages_user_from_sender(user, sender) 
            self.db_manager.change_message_status_into_read(self.current_user.username)
            return messages 
        else:
            return "Nie masz uprawnień do tej komendy"

    def read_new_message(self, command):
        if self.current_user.is_user_allowed_to_command(str(command)) and  self.current_user.is_logged:
            new_messages = self.db_manager.get_all_new_messages_user(self.current_user.username)
            self.db_manager.change_message_status_into_read(self.current_user.username)
            print(new_messages)
            response = []
            for message in new_messages:
                response.append(f"Wiadomosc od: {message[1]}: {message[0]} / wysłano: {message[2]}")
            if response:
                return "\n".join(response)
            else:
                return "Nie masz nowych wiadomości"
        else:
            response =  "Nie masz uprawnień do tej komendy"
        return response

    def get_user_info(self, command, user):
        #print(self.current_user.is_user_allowed_to_command(str(command)))
        #print(self.current_user.is_logged)
        if self.current_user.is_user_allowed_to_command(str(command)) and self.current_user.is_logged:   
            messages = self.db_manager.get_user_info(user) 
            response = messages 
        else:
            response = "Nie masz uprawnień do tej komendy"
        return response

    def delete_user(self, command, username):
        if self.current_user.is_user_allowed_to_command(str(command)) and  self.current_user.is_logged and username != self.current_user.username:
            is_delete = self.db_manager.delete_user_from_db(username) 
            if is_delete:
                response = "Użytkownik został usunięty"
            else:
                response = "Użytkownik nie został usunięty"
        else:
            response = "Nie masz uprawnień do tej komendy"
        return response

    def create_new_user(self,command, username, password):
        if self.current_user.is_user_allowed_to_command(str(command)) and not self.current_user.is_logged:
            if self.db_manager.is_user_in_db(username):
                response = "Użytkownik już istnieje"
            elif len(password) < 2 and len(username) < 2:
                response = "Hasło musi mieć minimum 2 znaki"
            else:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                user = {
                    "id": self.generate_id_user(),
                    "username": username,
                    "role": "user",
                    "password": hashed_password.decode('utf-8'),
                    "login_time": None,
                    "create_time": datetime.now().isoformat()
                }
                #print(user)
                is_add = self.db_manager.add_user_into_db(user)
                if is_add:  
                    response = "Użytkownik został dodany do bazy danych"
                else:
                    response = "Użytkownik nie został dodany do bazy danych"
            
        else:
            response = "Nie masz uprawnień do tego komendy lub jestes juz zalogowany"
        return response

    def login_user(self, command, username, password):
        try:
            if not username or not password:
                return "Nazwa użytkownika i hasło nie mogą być puste"
                
            elif self.current_user.is_user_allowed_to_command(str(command)) and not self.current_user.is_logged:
                stored_password = self.db_manager.get_user_password(username)
                stored_role = self.db_manager.get_user_role(username)
                #print(stored_password)
                if stored_password and bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    self.db_manager.change_login_time_in_db(username)
                    #print(self.db_manager.change_login_time_in_db(username))
                    self.current_user.username = username
                    self.current_user.password = stored_password
                    self.current_user.is_logged = True
                    self.current_user.role = stored_role
            
                    response = "Użytkownik został zalogowany"
                else:
                    response = "Nieprawidłowa nazwa użytkownika lub hasło"
            else:
                response = "Nie masz uprawnień do tej komendy lub jesteś już zalogowany"
            return response
            
        except UnicodeEncodeError:
            return "Hasło zawiera nieprawidłowe znaki"
        except Exception as e:
            return f"Wystąpił nieoczekiwany błąd: {str(e)}"

    def logout_user(self, command):
        if self.current_user.is_user_allowed_to_command(str(command)) and self.current_user.is_logged:
            self.current_user.is_logged = False
            return "Uzytkownik został wylogowany"
        return "Uzytkownik nie był zalogowany"

    def edit_user_role(self, command, username, new_role):
        is_user_in_db = self.db_manager.is_user_in_db(username)
        if self.current_user.is_user_allowed_to_command(command) and self.current_user.is_logged and is_user_in_db:
            self.db_manager.edit_user_role_in_db(username, new_role)
            return "Rola zostala zmieniona"
        else:
            return "Nie masz uprawnień do tej komendy lub użytkownik nie istnieje"
        
    def generate_id_user(self):
        return int(time.time() * 1000)
    
    def generate_id_message(self):
        return int(time.time() * 1000)



