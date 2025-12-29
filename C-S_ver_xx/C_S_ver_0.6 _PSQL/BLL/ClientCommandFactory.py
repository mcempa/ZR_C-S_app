from BLL.CommandFactory import CommandFactory
from Models.MessageProtocol import RequestDTO, MessageProtocol

class ClientCommandFactory(CommandFactory):
    """Manager dla strony klienta - tworzy żądania do wysłania na serwer"""
    
    def __init__(self):
        super().__init__()

    def _create_request(self, command, data_dict):
        """Tworzy uproszczone żądanie DTO"""
        return MessageProtocol.create_request(command, data_dict)

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
        return MessageProtocol.create_error_response(f"Nieznana komenda: {command}", "UNKNOWN_COMMAND")

    # ============= BUSINESS LOGIC ONLY =============
    # UI logic moved to UI/ClientUIHandler.py
    
    def is_valid_command(self, command):
        """Check if command is valid"""
        return command in self.command_map
    
    def create_request(self, command, data_input):
        """Create request for given command and data"""
        if not self.is_valid_command(command):
            return self._handle_unknown_command(command)
        
        if len(data_input) > 0:
            return self.command_map[command](command, **data_input)
        else:
            return self.command_map[command](command)
