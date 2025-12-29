class UserClientManager:
    def __init__(self):
        self.command_map = {
                "send"   : self.request_send_message,
                "read"   : self.request_read_new_message,
                "read-u" : self.request_read_message_current_user_from_sender,
                "read-a" : self.request_read_all_message_current_user,
                "read-o" : self.request_read_message_user_from_sender,
                "login"  : self.request_login,
                "logout" : self.request_logout,
                "help"   : self.request_get_help,
                "info"   : self.request_get_user_info,
                "create" : self.request_create_new_user,
                "delete" : self.request_delete_user,
                "edit"   : self.request_edit_user_role,          
        } 

    def prepere_request(self):
        command = input("Podaj komendę: ").lower()
        
        if command in ("help", "read-a", "read", "logout"):
            data_input = []

        elif command in ("login", "create"):
            data_input_login = input("Podaj nazwę uzytkownika: ").strip().lower()
            data_input_password = input("Podaj hasło uzytkownika: ").strip()
            data_input = [data_input_login, data_input_password]

        elif command in ("send"):
            data_input_login = input("Odbiorca wiadomości - podaj nazwę uzytkownika: ").strip().lower()
            data_input_password = input("Wpisz treść wiadomości: ").strip()
            data_input = [data_input_login, data_input_password]
        
        elif command in ("read-u"):
            data_input = [input("Podaj nazwę użytkownika, od którego wiadomoścu chesz przeglądać: ")]

        elif command in ("read-o"):
            data_input_user = input("Podaj nazwę użytkownika, którego wiadomości chesz przeglądać: ").strip().lower()
            data_input_sander = input("Podaj nazwę nadawcy wiadomości: ").strip().lower()
            data_input = [data_input_user, data_input_sander]

        elif command in ("edit"):
            data_input_user = input("Podaj nazwę użytkownika, którego rolę chesz zmienić: ").strip().lower()
            data_input_role = input("Nowa rola: ").strip().lower()
            data_input = [data_input_user, data_input_role]
            
        elif command in ("info", "delete"):
            data_input = [input("Podaj nazwę użytkownika: ").lower()]
        
        elif command not in self.command_map or not command:
            data_input = []
            print("Komenda nie istnieje")
        return command, data_input    
    
    
    def request_login(self, command, username, password):
        request = [str(command), {
            "username": username,
            "password": password
        }]
        return self.set_format(request)

    def request_logout(self, command):
        request = [str(command), {}]
        return self.set_format(request)
        
    def request_create_new_user(self,command, username, password):
        request = [str(command), {
            "username": username,
            "password": password
        }]
        return self.set_format(request)
    
    def request_send_message(self, command, text, reciver):
        request =[str(command), {
            "text": text,
            "username": reciver
        }]
        return self.set_format(request)

    def request_read_message_user_from_sender(self, command, username, sender):
        request = [str(command), {
            "username": username,
            "sender": sender
        }]
        #print(request)
        return self.set_format(request)
    
    def request_read_new_message(self, command):
        request = [str(command), {}]
        return self.set_format(request)

    def request_read_message_current_user_from_sender(self, command, sender):
        request = [str(command), {
            "username": sender
        }]
        return self.set_format(request)

    def request_read_all_message_current_user(self, command):
        request = [str(command), {}]
        return self.set_format(request)
    
    def request_get_help(self, command):
        request = [str(command), {}]
        return self.set_format(request)
    
    def request_get_user_info(self, command, username):
        request = [str(command), {
            "username": username
        }]
        return self.set_format(request)
    
    def request_delete_user(self, command, username):
        request = [str(command), {
            "username": username
        }]
        return self.set_format(request)
    
    def request_edit_user_role(self,command, username, new_role):
        request = [str(command), {
            "username": username,
            "new_role": new_role
        }]
        return self.set_format(request)

    def set_format(self, request):  #przygotowany na potrzeby zmiany formatu wysyłania requestu do serwera
        list_data = request
        return list_data











