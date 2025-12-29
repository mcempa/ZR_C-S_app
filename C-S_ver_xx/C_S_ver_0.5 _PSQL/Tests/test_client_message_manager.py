import unittest
from unittest.mock import Mock, patch, call
from BLL.ClientMessageManager import ClientMessageManager

class TestClientMessageManager(unittest.TestCase):
    
    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem"""
        self.manager = ClientMessageManager()

    def test_constructor_initializes_properly(self):
        """Test czy konstruktor poprawnie inicjalizuje klasę"""
        self.assertIsInstance(self.manager, ClientMessageManager)
        self.assertIsInstance(self.manager.command_map, dict)
        
        # Sprawdzenie czy dziedziczy po BaseMessageManager
        from BLL.BaseMessageManager import BaseMessageManager
        self.assertIsInstance(self.manager, BaseMessageManager)

    def test_create_request_basic_functionality(self):
        """Test podstawowej funkcjonalności _create_request"""
        result = self.manager._create_request("test_command", {"key": "value"})
        expected = ["test_command", {"key": "value"}]
        self.assertEqual(result, expected)

    def test_create_request_with_empty_data(self):
        """Test _create_request z pustymi danymi"""
        result = self.manager._create_request("empty_command", {})
        expected = ["empty_command", {}]
        self.assertEqual(result, expected)

    def test_create_request_command_as_string(self):
        """Test czy komenda jest konwertowana na string"""
        result = self.manager._create_request(123, {"data": "test"})
        expected = ["123", {"data": "test"}]
        self.assertEqual(result, expected)

    def test_handle_send_message(self):
        """Test obsługi wysyłania wiadomości"""
        result = self.manager.handle_send_message("send", receiver="john", text="Hello world")
        expected = ["send", {"receiver": "john", "text": "Hello world"}]
        self.assertEqual(result, expected)

    def test_handle_send_message_with_none_values(self):
        """Test wysyłania wiadomości z wartościami None"""
        result = self.manager.handle_send_message("send", receiver=None, text=None)
        expected = ["send", {"receiver": None, "text": None}]
        self.assertEqual(result, expected)

    def test_handle_send_message_with_kwargs(self):
        """Test wysyłania wiadomości z dodatkowymi argumentami kwargs"""
        result = self.manager.handle_send_message("send", receiver="john", text="Hello", extra_param="ignored")
        expected = ["send", {"receiver": "john", "text": "Hello"}]
        self.assertEqual(result, expected)

    def test_handle_read_new_message(self):
        """Test obsługi odczytu nowych wiadomości"""
        result = self.manager.handle_read_new_message("read")
        expected = ["read", {}]
        self.assertEqual(result, expected)

    def test_handle_read_new_message_with_kwargs(self):
        """Test odczytu nowych wiadomości z argumentami kwargs"""
        result = self.manager.handle_read_new_message("read", ignored_param="value")
        expected = ["read", {}]
        self.assertEqual(result, expected)

    def test_handle_read_message_current_user_from_sender(self):
        """Test obsługi odczytu wiadomości od konkretnego nadawcy"""
        result = self.manager.handle_read_message_current_user_from_sender("read-u", sender="alice")
        expected = ["read-u", {"sender": "alice"}]
        self.assertEqual(result, expected)

    def test_handle_read_message_current_user_from_sender_none(self):
        """Test odczytu wiadomości z None jako nadawca"""
        result = self.manager.handle_read_message_current_user_from_sender("read-u", sender=None)
        expected = ["read-u", {"sender": None}]
        self.assertEqual(result, expected)

    def test_handle_read_all_message_current_user(self):
        """Test obsługi odczytu wszystkich wiadomości użytkownika"""
        result = self.manager.handle_read_all_message_current_user("read-a")
        expected = ["read-a", {}]
        self.assertEqual(result, expected)

    def test_handle_read_message_user_from_sender(self):
        """Test obsługi odczytu wiadomości konkretnego użytkownika od nadawcy"""
        result = self.manager.handle_read_message_user_from_sender("read-o", username="bob", sender="alice")
        expected = ["read-o", {"username": "bob", "sender": "alice"}]
        self.assertEqual(result, expected)

    def test_handle_read_message_user_from_sender_partial_params(self):
        """Test z tylko jednym parametrem"""
        result = self.manager.handle_read_message_user_from_sender("read-o", username="bob")
        expected = ["read-o", {"username": "bob", "sender": None}]
        self.assertEqual(result, expected)

    def test_handle_login(self):
        """Test obsługi logowania"""
        result = self.manager.handle_login("login", username="testuser", password="secret123")
        expected = ["login", {"username": "testuser", "password": "secret123"}]
        self.assertEqual(result, expected)

    def test_handle_login_missing_params(self):
        """Test logowania z brakującymi parametrami"""
        result = self.manager.handle_login("login", username="testuser")
        expected = ["login", {"username": "testuser", "password": None}]
        self.assertEqual(result, expected)

    def test_handle_logout(self):
        """Test obsługi wylogowania"""
        result = self.manager.handle_logout("logout")
        expected = ["logout", {}]
        self.assertEqual(result, expected)

    def test_handle_get_help(self):
        """Test obsługi pomocy"""
        result = self.manager.handle_get_help("help")
        expected = ["help", {}]
        self.assertEqual(result, expected)

    def test_handle_get_user_info(self):
        """Test obsługi informacji o użytkowniku"""
        result = self.manager.handle_get_user_info("info", username="testuser")
        expected = ["info", {"username": "testuser"}]
        self.assertEqual(result, expected)

    def test_handle_get_user_info_no_username(self):
        """Test informacji o użytkowniku bez nazwy"""
        result = self.manager.handle_get_user_info("info")
        expected = ["info", {"username": None}]
        self.assertEqual(result, expected)

    def test_handle_create_new_user(self):
        """Test obsługi tworzenia nowego użytkownika"""
        result = self.manager.handle_create_new_user("create", username="newuser", password="newpass")
        expected = ["create", {"username": "newuser", "password": "newpass"}]
        self.assertEqual(result, expected)

    def test_handle_create_new_user_partial_params(self):
        """Test tworzenia użytkownika z brakującymi parametrami"""
        result = self.manager.handle_create_new_user("create", username="newuser")
        expected = ["create", {"username": "newuser", "password": None}]
        self.assertEqual(result, expected)

    def test_handle_delete_user(self):
        """Test obsługi usuwania użytkownika"""
        result = self.manager.handle_delete_user("delete", username="userToDelete")
        expected = ["delete", {"username": "userToDelete"}]
        self.assertEqual(result, expected)

    def test_handle_delete_user_no_username(self):
        """Test usuwania użytkownika bez nazwy"""
        result = self.manager.handle_delete_user("delete")
        expected = ["delete", {"username": None}]
        self.assertEqual(result, expected)

    def test_handle_edit_user_role(self):
        """Test obsługi edycji roli użytkownika"""
        result = self.manager.handle_edit_user_role("edit", username="testuser", new_role="admin")
        expected = ["edit", {"username": "testuser", "new_role": "admin"}]
        self.assertEqual(result, expected)

    def test_handle_edit_user_role_partial_params(self):
        """Test edycji roli z brakującymi parametrami"""
        result = self.manager.handle_edit_user_role("edit", username="testuser")
        expected = ["edit", {"username": "testuser", "new_role": None}]
        self.assertEqual(result, expected)

    def test_handle_unknown_command(self):
        """Test obsługi nieznanej komendy"""
        result = self.manager._handle_unknown_command("unknown_cmd")
        expected = ["error", {"message": "Nieznana komenda: unknown_cmd"}]
        self.assertEqual(result, expected)

    def test_handle_unknown_command_various_inputs(self):
        """Test nieznanej komendy z różnymi wejściami"""
        test_cases = [
            ("", "Nieznana komenda: "),
            ("CAPS", "Nieznana komenda: CAPS"),
            ("123", "Nieznana komenda: 123"),
            ("special@chars", "Nieznana komenda: special@chars")
        ]
        
        for command, expected_message in test_cases:
            with self.subTest(command=command):
                result = self.manager._handle_unknown_command(command)
                expected = ["error", {"message": expected_message}]
                self.assertEqual(result, expected)

    def test_process_command_integration(self):
        """Test integracji z metodą process_command z klasy bazowej"""
        # Test znanej komendy
        result = self.manager.process_command("send", receiver="john", text="hello")
        expected = ["send", {"receiver": "john", "text": "hello"}]
        self.assertEqual(result, expected)
        
        # Test nieznanej komendy
        result = self.manager.process_command("unknown")
        expected = ["error", {"message": "Nieznana komenda: unknown"}]
        self.assertEqual(result, expected)

    @patch('builtins.input')
    def test_prepare_request_interactive_help(self, mock_input):
        """Test interaktywnego przygotowania żądania dla help"""
        mock_input.return_value = "help"
        
        command, data = self.manager.prepare_request_interactive()
        
        self.assertEqual(command, "help")
        self.assertEqual(data, {})

    @patch('builtins.input')
    def test_prepare_request_interactive_read_commands(self, mock_input):
        """Test interaktywnych komend read"""
        read_commands = ["read-a", "read", "logout"]
        
        for cmd in read_commands:
            with self.subTest(command=cmd):
                mock_input.return_value = cmd
                command, data = self.manager.prepare_request_interactive()
                self.assertEqual(command, cmd)
                self.assertEqual(data, {})

    @patch('builtins.input')
    def test_prepare_request_interactive_login(self, mock_input):
        """Test interaktywnego logowania"""
        mock_input.side_effect = ["login", "testuser", "testpass"]
        
        command, data = self.manager.prepare_request_interactive()
        
        self.assertEqual(command, "login")
        self.assertEqual(data, {"username": "testuser", "password": "testpass"})

    @patch('builtins.input')
    def test_prepare_request_interactive_create(self, mock_input):
        """Test interaktywnego tworzenia użytkownika"""
        mock_input.side_effect = ["create", "newuser", "newpass"]
        
        command, data = self.manager.prepare_request_interactive()
        
        self.assertEqual(command, "create")
        self.assertEqual(data, {"username": "newuser", "password": "newpass"})

    @patch('builtins.input')
    def test_prepare_request_interactive_send(self, mock_input):
        """Test interaktywnego wysyłania wiadomości"""
        mock_input.side_effect = ["send", "receiver", "test message"]
        
        command, data = self.manager.prepare_request_interactive()
        
        self.assertEqual(command, "send")
        self.assertEqual(data, {"receiver": "receiver", "text": "test message"})

    @patch('builtins.input')
    def test_prepare_request_interactive_read_u(self, mock_input):
        """Test interaktywnego czytania wiadomości od użytkownika"""
        mock_input.side_effect = ["read-u", "sender"]
        
        command, data = self.manager.prepare_request_interactive()
        
        self.assertEqual(command, "read-u")
        self.assertEqual(data, {"sender": "sender"})

    @patch('builtins.input')
    def test_prepare_request_interactive_read_o(self, mock_input):
        """Test interaktywnego czytania wiadomości innego użytkownika"""
        mock_input.side_effect = ["read-o", "username", "sender"]
        
        command, data = self.manager.prepare_request_interactive()
        
        self.assertEqual(command, "read-o")
        self.assertEqual(data, {"username": "username", "sender": "sender"})

    @patch('builtins.input')
    def test_prepare_request_interactive_edit(self, mock_input):
        """Test interaktywnej edycji roli"""
        mock_input.side_effect = ["edit", "username", "admin"]
        
        command, data = self.manager.prepare_request_interactive()
        
        self.assertEqual(command, "edit")
        self.assertEqual(data, {"username": "username", "new_role": "admin"})

    @patch('builtins.input')
    def test_prepare_request_interactive_info_delete(self, mock_input):
        """Test interaktywnych komend info i delete"""
        commands = ["info", "delete"]
        
        for cmd in commands:
            with self.subTest(command=cmd):
                mock_input.side_effect = [cmd, "username"]
                command, data = self.manager.prepare_request_interactive()
                self.assertEqual(command, cmd)
                self.assertEqual(data, {"username": "username"})

    @patch('builtins.input')
    @patch('builtins.print')
    def test_prepare_request_interactive_unknown_command(self, mock_print, mock_input):
        """Test interaktywnej obsługi nieznanej komendy"""
        mock_input.return_value = "unknown"
        
        command, data = self.manager.prepare_request_interactive()
        
        self.assertEqual(command, "unknown")
        self.assertEqual(data, {})
        mock_print.assert_called_once_with("Komenda nie istnieje")

    @patch('builtins.input')
    def test_prepare_request_interactive_case_insensitive(self, mock_input):
        """Test case insensitive dla interaktywnych komend"""
        mock_input.side_effect = ["HELP"]  # uppercase
        
        command, data = self.manager.prepare_request_interactive()
        
        self.assertEqual(command, "help")  # powinno być skonwertowane na lowercase
        self.assertEqual(data, {})

    @patch('builtins.input')
    def test_prepare_request_interactive_whitespace_handling(self, mock_input):
        """Test obsługi białych znaków w interaktywnych komendach"""
        mock_input.side_effect = ["  help  ", "  testuser  ", "  testpass  "]
        
        command, data = self.manager.prepare_request_interactive()
        
        self.assertEqual(command, "help")

    def test_get_login_input(self):
        """Test metody _get_login_input"""
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = ["TestUser", "TestPass"]
            result = self.manager._get_login_input()
            expected = {"username": "testuser", "password": "TestPass"}
            self.assertEqual(result, expected)

    def test_get_create_input(self):
        """Test metody _get_create_input"""
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = ["NewUser", "NewPass"]
            result = self.manager._get_create_input()
            expected = {"username": "newuser", "password": "NewPass"}
            self.assertEqual(result, expected)

    def test_get_send_message_input(self):
        """Test metody _get_send_message_input"""
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = ["Receiver", "Hello World"]
            result = self.manager._get_send_message_input()
            expected = {"receiver": "receiver", "text": "Hello World"}
            self.assertEqual(result, expected)

    def test_get_sender_input(self):
        """Test metody _get_sender_input"""
        with patch('builtins.input') as mock_input:
            mock_input.return_value = "SenderName"
            result = self.manager._get_sender_input()
            expected = {"sender": "sendername"}
            self.assertEqual(result, expected)

    def test_get_read_message_input(self):
        """Test metody _get_read_message_input"""
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = ["Username", "Sender"]
            result = self.manager._get_read_message_input()
            expected = {"username": "username", "sender": "sender"}
            self.assertEqual(result, expected)

    def test_get_edit_role_input(self):
        """Test metody _get_edit_role_input"""
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = ["Username", "Admin"]
            result = self.manager._get_edit_role_input()
            expected = {"username": "username", "new_role": "admin"}
            self.assertEqual(result, expected)

    def test_get_username_input(self):
        """Test metody _get_username_input"""
        with patch('builtins.input') as mock_input:
            mock_input.return_value = "TestUser"
            result = self.manager._get_username_input()
            expected = {"username": "testuser"}
            self.assertEqual(result, expected)

    def test_input_methods_whitespace_handling(self):
        """Test obsługi białych znaków we wszystkich metodach input"""
        input_methods = [
            ('_get_login_input', ["  user  ", "  pass  "], {"username": "user", "password": "  pass  "}),
            ('_get_create_input', ["  user  ", "  pass  "], {"username": "user", "password": "  pass  "}),
            ('_get_send_message_input', ["  receiver  ", "  message  "], {"receiver": "receiver", "text": "  message  "}),
            ('_get_sender_input', ["  sender  "], {"sender": "sender"}),
            ('_get_read_message_input', ["  user  ", "  sender  "], {"username": "user", "sender": "sender"}),
            ('_get_edit_role_input', ["  user  ", "  role  "], {"username": "user", "new_role": "role"}),
            ('_get_username_input', ["  user  "], {"username": "user"})
        ]
        
        for method_name, inputs, expected in input_methods:
            with self.subTest(method=method_name):
                with patch('builtins.input') as mock_input:
                    mock_input.side_effect = inputs
                    method = getattr(self.manager, method_name)
                    result = method()
                    self.assertEqual(result, expected)

    def test_all_handler_methods_exist(self):
        """Test czy wszystkie metody handler istnieją i są callable"""
        expected_handlers = [
            'handle_send_message',
            'handle_read_new_message',
            'handle_read_message_current_user_from_sender',
            'handle_read_all_message_current_user',
            'handle_read_message_user_from_sender',
            'handle_login',
            'handle_logout',
            'handle_get_help',
            'handle_get_user_info',
            'handle_create_new_user',
            'handle_delete_user',
            'handle_edit_user_role'
        ]
        
        for handler_name in expected_handlers:
            with self.subTest(handler=handler_name):
                self.assertTrue(hasattr(self.manager, handler_name))
                handler = getattr(self.manager, handler_name)
                self.assertTrue(callable(handler))

    def test_command_consistency_between_map_and_handlers(self):
        """Test spójności między command_map a rzeczywistymi handlerami"""
        for command, handler in self.manager.command_map.items():
            with self.subTest(command=command):
                # Sprawdź czy handler jest callable
                self.assertTrue(callable(handler))
                
                # Sprawdź czy wywołanie handlera zwraca oczekiwany format
                result = handler(command)
                self.assertIsInstance(result, list)
                self.assertEqual(len(result), 2)
                self.assertEqual(result[0], command)
                self.assertIsInstance(result[1], dict)

if __name__ == '__main__':
    unittest.main()