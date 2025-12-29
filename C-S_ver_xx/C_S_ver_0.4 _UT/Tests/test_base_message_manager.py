import unittest
from unittest.mock import Mock, patch
from BLL.BaseMessageManager import BaseMessageManager
from config import FORBIDDEN_CHARS

class TestableMessageManager(BaseMessageManager):
    """Konkretna implementacja BaseMessageManager dla celów testowych"""
    
    def __init__(self):
        super().__init__()
        # Tworzenie mocków dla trackowania wywołań
        self.mock_send = Mock(return_value="send_result")
        self.mock_read = Mock(return_value="read_result")
        self.mock_read_u = Mock(return_value="read_u_result")
        self.mock_read_a = Mock(return_value="read_a_result")
        self.mock_read_o = Mock(return_value="read_o_result")
        self.mock_login = Mock(return_value="login_result")
        self.mock_logout = Mock(return_value="logout_result")
        self.mock_help = Mock(return_value="help_result")
        self.mock_info = Mock(return_value="info_result")
        self.mock_create = Mock(return_value="create_result")
        self.mock_delete = Mock(return_value="delete_result")
        self.mock_edit = Mock(return_value="edit_result")
        self.mock_unknown = Mock(return_value="unknown_command_result")

    def handle_send_message(self, command, *args, **kwargs):
        return self.mock_send(command, *args, **kwargs)
    
    def handle_read_new_message(self, command, *args, **kwargs):
        return self.mock_read(command, *args, **kwargs)
    
    def handle_read_message_current_user_from_sender(self, command, *args, **kwargs):
        return self.mock_read_u(command, *args, **kwargs)
    
    def handle_read_all_message_current_user(self, command, *args, **kwargs):
        return self.mock_read_a(command, *args, **kwargs)
    
    def handle_read_message_user_from_sender(self, command, *args, **kwargs):
        return self.mock_read_o(command, *args, **kwargs)
    
    def handle_login(self, command, *args, **kwargs):
        return self.mock_login(command, *args, **kwargs)
    
    def handle_logout(self, command, *args, **kwargs):
        return self.mock_logout(command, *args, **kwargs)
    
    def handle_get_help(self, command, *args, **kwargs):
        return self.mock_help(command, *args, **kwargs)
    
    def handle_get_user_info(self, command, *args, **kwargs):
        return self.mock_info(command, *args, **kwargs)
    
    def handle_create_new_user(self, command, *args, **kwargs):
        return self.mock_create(command, *args, **kwargs)
    
    def handle_delete_user(self, command, *args, **kwargs):
        return self.mock_delete(command, *args, **kwargs)
    
    def handle_edit_user_role(self, command, *args, **kwargs):
        return self.mock_edit(command, *args, **kwargs)
    
    def _handle_unknown_command(self, command):
        return self.mock_unknown(command)

class TestBaseMessageManager(unittest.TestCase):
    
    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem"""
        self.manager = TestableMessageManager()

    def test_constructor_initializes_command_map(self):
        """Test czy konstruktor inicjalizuje command_map"""
        expected_commands = [
            "send", "read", "read-u", "read-a", "read-o",
            "login", "logout", "help", "info", "create", "delete", "edit"
        ]
        
        self.assertIsInstance(self.manager.command_map, dict)
        
        for command in expected_commands:
            self.assertIn(command, self.manager.command_map)
            self.assertTrue(callable(self.manager.command_map[command]))

    def test_command_map_completeness(self):
        """Test czy command_map zawiera wszystkie oczekiwane komendy"""
        expected_mapping = {
            "send": "handle_send_message",
            "read": "handle_read_new_message", 
            "read-u": "handle_read_message_current_user_from_sender",
            "read-a": "handle_read_all_message_current_user",
            "read-o": "handle_read_message_user_from_sender",
            "login": "handle_login",
            "logout": "handle_logout",
            "help": "handle_get_help",
            "info": "handle_get_user_info",
            "create": "handle_create_new_user",
            "delete": "handle_delete_user",
            "edit": "handle_edit_user_role"
        }
        
        self.assertEqual(len(self.manager.command_map), len(expected_mapping))
        
        for command, method_name in expected_mapping.items():
            self.assertIn(command, self.manager.command_map)
            # Sprawdzenie czy metoda istnieje
            self.assertTrue(hasattr(self.manager, method_name))

    def test_process_command_known_command(self):
        """Test przetwarzania znanej komendy"""
        result = self.manager.process_command("send", receiver="test_user", text="hello")
        
        self.assertEqual(result, "send_result")
        self.manager.mock_send.assert_called_once_with("send", receiver="test_user", text="hello")

    def test_process_command_all_known_commands(self):
        """Test przetwarzania wszystkich znanych komend"""
        test_cases = [
            ("send", "send_result", "mock_send"),
            ("read", "read_result", "mock_read"),
            ("read-u", "read_u_result", "mock_read_u"),
            ("read-a", "read_a_result", "mock_read_a"),
            ("read-o", "read_o_result", "mock_read_o"),
            ("login", "login_result", "mock_login"),
            ("logout", "logout_result", "mock_logout"),
            ("help", "help_result", "mock_help"),
            ("info", "info_result", "mock_info"),
            ("create", "create_result", "mock_create"),
            ("delete", "delete_result", "mock_delete"),
            ("edit", "edit_result", "mock_edit")
        ]
        
        for command, expected_result, mock_name in test_cases:
            with self.subTest(command=command):
                result = self.manager.process_command(command, test_param="test")
                self.assertEqual(result, expected_result)
                mock_method = getattr(self.manager, mock_name)
                mock_method.assert_called_with(command, test_param="test")

    def test_process_command_unknown_command(self):
        """Test przetwarzania nieznanej komendy"""
        result = self.manager.process_command("unknown_cmd")
        
        self.assertEqual(result, "unknown_command_result")
        self.manager.mock_unknown.assert_called_once_with("unknown_cmd")

    def test_process_command_with_args_and_kwargs(self):
        """Test przetwarzania komendy z argumentami pozycyjnymi i nazwanymi"""
        self.manager.process_command("send", "arg1", "arg2", kwarg1="value1", kwarg2="value2")
        
        self.manager.mock_send.assert_called_once_with(
            "send", "arg1", "arg2", kwarg1="value1", kwarg2="value2"
        )

    def test_validate_string_normal_text(self):
        """Test walidacji normalnego tekstu"""
        result = self.manager._validate_string("Hello world")
        self.assertEqual(result, "Hello world")

    def test_validate_string_with_forbidden_chars(self):
        """Test walidacji tekstu z zabronionymi znakami"""
        test_text = 'Hello "world" with \'quotes\' and {brackets} and [arrays] and ;semicolon'
        result = self.manager._validate_string(test_text)
        
        # Sprawdzenie czy wszystkie zabronione znaki zostały usunięte
        for char in FORBIDDEN_CHARS:
            self.assertNotIn(char, result)
        
        expected = "Hello world with quotes and brackets and arrays and semicolon"
        self.assertEqual(result, expected)

    def test_validate_string_each_forbidden_char(self):
        """Test walidacji dla każdego zabronionego znaku osobno"""
        for char in FORBIDDEN_CHARS:
            with self.subTest(char=char):
                test_text = f"test{char}text"
                result = self.manager._validate_string(test_text)
                self.assertEqual(result, "testtext")
                self.assertNotIn(char, result)

    def test_validate_string_with_whitespace(self):
        """Test walidacji tekstu z białymi znakami"""
        test_cases = [
            ("  hello  ", "hello"),
            ("\thello\t", "hello"),
            ("\nhello\n", "hello"),
            ("  hello world  ", "hello world"),
            ("", "")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=repr(input_text)):
                result = self.manager._validate_string(input_text)
                self.assertEqual(result, expected)

    def test_validate_string_non_string_input(self):
        """Test walidacji dla nie-stringowych danych wejściowych"""
        test_cases = [
            (123, "123"),
            (45.67, "45.67"),
            (True, "True"),
            (False, "False"),
            ([1, 2, 3], "1, 2, 3")  # Nawiasy [] są w FORBIDDEN_CHARS i zostają usunięte
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = self.manager._validate_string(input_value)
                self.assertEqual(result, expected)

    def test_validate_string_conversion_error(self):
        """Test obsługi błędu konwersji na string"""
        # Mock obiektu który nie może być przekonwertowany na string
        mock_obj = Mock()
        mock_obj.__str__ = Mock(side_effect=Exception("Conversion error"))
        
        with self.assertRaises(ValueError) as context:
            self.manager._validate_string(mock_obj)
        
        self.assertIn("Nie można przekonwertować wartości na tekst", str(context.exception))

    def test_validate_string_none_input(self):
        """Test walidacji dla None"""
        result = self.manager._validate_string(None)
        self.assertEqual(result, "None")

    def test_validate_string_empty_string(self):
        """Test walidacji pustego stringa"""
        result = self.manager._validate_string("")
        self.assertEqual(result, "")

    def test_validate_string_only_forbidden_chars(self):
        """Test walidacji tekstu składającego się tylko z zabronionych znaków"""
        forbidden_text = ''.join(FORBIDDEN_CHARS)
        result = self.manager._validate_string(forbidden_text)
        self.assertEqual(result, "")

    def test_validate_string_mixed_content(self):
        """Test walidacji mieszanej zawartości"""
        test_text = '  Hello "world" with numbers 123 and symbols!@#$%  '
        result = self.manager._validate_string(test_text)
        
        # Powinien usunąć tylko zabronione znaki i przyciąć białe znaki
        self.assertNotIn('"', result)
        self.assertEqual(result, 'Hello world with numbers 123 and symbols!@#$%')

    def test_process_command_case_sensitivity(self):
        """Test czy komendy są case-sensitive"""
        # Wielkie litery powinny być traktowane jako nieznane komendy
        result = self.manager.process_command("SEND")
        self.assertEqual(result, "unknown_command_result")
        
        result = self.manager.process_command("Send")
        self.assertEqual(result, "unknown_command_result")

    def test_process_command_empty_string(self):
        """Test przetwarzania pustej komendy"""
        result = self.manager.process_command("")
        self.assertEqual(result, "unknown_command_result")
        self.manager.mock_unknown.assert_called_with("")

    def test_process_command_none_command(self):
        """Test przetwarzania None jako komendy"""
        result = self.manager.process_command(None)
        self.assertEqual(result, "unknown_command_result")
        self.manager.mock_unknown.assert_called_with(None)

    def test_validate_string_preserves_valid_special_chars(self):
        """Test czy walidacja zachowuje dozwolone znaki specjalne"""
        valid_special_chars = "!@#$%^&*()_+-=<>?/\\|~`"
        test_text = f"Hello{valid_special_chars}World"
        result = self.manager._validate_string(test_text)
        
        for char in valid_special_chars:
            self.assertIn(char, result, f"Valid special character '{char}' was removed")

    def test_command_map_immutability_during_runtime(self):
        """Test czy command_map nie zmienia się podczas wykonywania"""
        original_map = self.manager.command_map.copy()
        
        # Wykonanie kilku komend
        self.manager.process_command("send")
        self.manager.process_command("read")
        self.manager.process_command("unknown")
        
        # command_map powinien pozostać niezmieniony
        self.assertEqual(self.manager.command_map, original_map)

if __name__ == '__main__':
    unittest.main()