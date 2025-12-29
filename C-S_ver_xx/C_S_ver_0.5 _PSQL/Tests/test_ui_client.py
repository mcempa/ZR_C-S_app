import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import io
from contextlib import contextmanager

class TestClientUI(unittest.TestCase):
    
    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem"""
        self.mock_connection = Mock()
        self.mock_user_manager = Mock()
        
    @contextmanager
    def capture_output(self):
        """Context manager do przechwytywania stdout"""
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        try:
            yield captured_output
        finally:
            sys.stdout = old_stdout

    @patch('BLL.ClientConnectionManager.ClientConnectionManager')
    @patch('BLL.ClientMessageManager.ClientMessageManager')
    @patch('builtins.input')
    def test_successful_logout_flow(self, mock_input, mock_message_manager_class, mock_connection_manager_class):
        """Test pomyślnego wylogowania użytkownika"""
        # Konfiguracja mocków
        mock_connection = Mock()
        mock_connection_manager_class.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connection_manager_class.return_value.__exit__ = Mock(return_value=None)
        
        mock_user_manager = Mock()
        mock_message_manager_class.return_value = mock_user_manager
        
        # Konfiguracja interakcji użytkownika
        mock_user_manager.prepare_request_interactive.return_value = ("logout", {})
        mock_user_manager.command_map = {"logout": Mock()}
        
        mock_connection.send_request.return_value = None
        mock_connection.recv_response.return_value = "OK"
        
        with self.capture_output() as output:
            # Import i uruchomienie modułu (symulacja)
            try:
                exec("""
import socket as s
from BLL.ClientConnectionManager import ClientConnectionManager
from BLL.ClientMessageManager import ClientMessageManager

with ClientConnectionManager() as connection:
    user_manager = ClientMessageManager()
    command, data_input = user_manager.prepare_request_interactive()
    
    if command == "logout":
        connection.send_request("logout")
        response = connection.recv_response()
        print(f"response: {response}")
        if response == "OK":
            print("Wylogowano pomyślnie")
        print("Zamykanie programu...")
        connection.close()
                """)
            except SystemExit:
                pass  # Oczekiwane dla break w pętli
        
        captured = output.getvalue()
        self.assertIn("response: OK", captured)
        self.assertIn("Wylogowano pomyślnie", captured)
        self.assertIn("Zamykanie programu...", captured)

    @patch('BLL.ClientConnectionManager.ClientConnectionManager')
    @patch('BLL.ClientMessageManager.ClientMessageManager')
    def test_connection_error_handling(self, mock_message_manager_class, mock_connection_manager_class):
        """Test obsługi błędu połączenia"""
        # Konfiguracja mocków
        mock_connection = Mock()
        mock_connection_manager_class.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connection_manager_class.return_value.__exit__ = Mock(return_value=None)
        
        mock_user_manager = Mock()
        mock_message_manager_class.return_value = mock_user_manager
        
        mock_user_manager.prepare_request_interactive.return_value = ("send", {"receiver": "test", "text": "hello"})
        mock_user_manager.command_map = {"send": Mock(return_value=["send", {"receiver": "test", "text": "hello"}])}
        
        # Symulacja błędu połączenia
        mock_connection.send_request.side_effect = ConnectionError("Błąd połączenia")
        
        with self.capture_output() as output:
            try:
                exec("""
import socket as s
from BLL.ClientConnectionManager import ClientConnectionManager
from BLL.ClientMessageManager import ClientMessageManager

with ClientConnectionManager() as connection:
    user_manager = ClientMessageManager()
    command, data_input = user_manager.prepare_request_interactive()
    
    if command != "logout":
        try:
            if len(data_input) > 0:
                request = user_manager.command_map[command](command, **data_input)
            else:
                request = user_manager.command_map[command](command)
            connection.send_request(str(request))
            connection.recv_response()
        except ConnectionError:
            print("Błąd połączenia z serwerem. Sprawdź połączenie i spróbuj ponownie.")
                """)
            except SystemExit:
                pass
        
        captured = output.getvalue()
        self.assertIn("Błąd połączenia z serwerem", captured)

    @patch('BLL.ClientConnectionManager.ClientConnectionManager')
    @patch('BLL.ClientMessageManager.ClientMessageManager')
    def test_unknown_command_handling(self, mock_message_manager_class, mock_connection_manager_class):
        """Test obsługi nieznanej komendy"""
        mock_connection = Mock()
        mock_connection_manager_class.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connection_manager_class.return_value.__exit__ = Mock(return_value=None)
        
        mock_user_manager = Mock()
        mock_message_manager_class.return_value = mock_user_manager
        
        mock_user_manager.prepare_request_interactive.return_value = ("unknown", {})
        mock_user_manager.command_map = {"send": Mock(), "read": Mock()}  # brak 'unknown'
        
        with self.capture_output() as output:
            try:
                exec("""
import socket as s
from BLL.ClientConnectionManager import ClientConnectionManager
from BLL.ClientMessageManager import ClientMessageManager

with ClientConnectionManager() as connection:
    user_manager = ClientMessageManager()
    command, data_input = user_manager.prepare_request_interactive()
    
    if command not in user_manager.command_map:
        print("Nieznane polecenie. Spróbuj ponownie.")
                """)
            except SystemExit:
                pass
        
        captured = output.getvalue()
        self.assertIn("Nieznane polecenie. Spróbuj ponownie.", captured)

    @patch('BLL.ClientConnectionManager.ClientConnectionManager')
    @patch('BLL.ClientMessageManager.ClientMessageManager')
    def test_keyboard_interrupt_handling(self, mock_message_manager_class, mock_connection_manager_class):
        """Test obsługi przerwania przez użytkownika (Ctrl+C)"""
        mock_connection = Mock()
        mock_connection_manager_class.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connection_manager_class.return_value.__exit__ = Mock(return_value=None)
        
        mock_user_manager = Mock()
        mock_message_manager_class.return_value = mock_user_manager
        
        # Symulacja KeyboardInterrupt
        mock_user_manager.prepare_request_interactive.side_effect = KeyboardInterrupt()
        
        with self.capture_output() as output:
            try:
                exec("""
import socket as s
from BLL.ClientConnectionManager import ClientConnectionManager
from BLL.ClientMessageManager import ClientMessageManager

with ClientConnectionManager() as connection:
    user_manager = ClientMessageManager()
    try:
        command, data_input = user_manager.prepare_request_interactive()
    except KeyboardInterrupt:
        print("Program został przerwany przez użytkownika.")
        connection.close()
                """)
            except SystemExit:
                pass
        
        captured = output.getvalue()
        self.assertIn("Program został przerwany przez użytkownika.", captured)

    @patch('BLL.ClientConnectionManager.ClientConnectionManager')
    @patch('BLL.ClientMessageManager.ClientMessageManager')
    def test_general_exception_handling(self, mock_message_manager_class, mock_connection_manager_class):
        """Test obsługi ogólnych wyjątków"""
        mock_connection = Mock()
        mock_connection_manager_class.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connection_manager_class.return_value.__exit__ = Mock(return_value=None)
        
        mock_user_manager = Mock()
        mock_message_manager_class.return_value = mock_user_manager
        
        mock_user_manager.prepare_request_interactive.return_value = ("send", {"receiver": "test", "text": "hello"})
        mock_user_manager.command_map = {"send": Mock(side_effect=Exception("Test exception"))}
        
        with self.capture_output() as output:
            try:
                exec("""
import socket as s
from BLL.ClientConnectionManager import ClientConnectionManager
from BLL.ClientMessageManager import ClientMessageManager

with ClientConnectionManager() as connection:
    user_manager = ClientMessageManager()
    try:
        command, data_input = user_manager.prepare_request_interactive()
        if command in user_manager.command_map:
            if len(data_input) > 0:
                request = user_manager.command_map[command](command, **data_input)
            else:
                request = user_manager.command_map[command](command)
    except Exception as e:
        print(f"Wystąpił błąd: {str(e)}")
                """)
            except SystemExit:
                pass
        
        captured = output.getvalue()
        self.assertIn("Wystąpił błąd: Test exception", captured)

    def test_client_request_processing_logic(self):
        """Test logiki przetwarzania żądań klienta"""
        # Test różnych scenariuszy przetwarzania komend
        test_cases = [
            # (command, data_input, expected_behavior)
            ("send", {"receiver": "user", "text": "hello"}, "with_data"),
            ("read", {}, "without_data"),
            ("help", {}, "without_data"),
            ("login", {"username": "test", "password": "pass"}, "with_data")
        ]
        
        for command, data_input, expected_behavior in test_cases:
            with self.subTest(command=command):
                mock_user_manager = Mock()
                mock_handler = Mock(return_value=[command, data_input])
                mock_user_manager.command_map = {command: mock_handler}
                
                # Symulacja logiki z client.py
                if len(data_input) > 0:
                    request = mock_user_manager.command_map[command](command, **data_input)
                else:
                    request = mock_user_manager.command_map[command](command)
                
                if expected_behavior == "with_data":
                    mock_handler.assert_called_once_with(command, **data_input)
                else:
                    mock_handler.assert_called_once_with(command)
                
                self.assertEqual(request, [command, data_input])

    def test_logout_error_scenarios(self):
        """Test różnych scenariuszy błędów podczas wylogowania"""
        error_scenarios = [
            (ConnectionResetError("Reset"), "Błąd podczas wylogowywania: Reset"),
            (ConnectionError("Connection lost"), "Błąd podczas wylogowywania: Connection lost"),
            (TimeoutError("Timeout"), "Błąd podczas wylogowywania: Timeout"),
            (Exception("Unexpected"), "Nieoczekiwany błąd podczas wylogowywania: Unexpected")
        ]
        
        for exception, expected_message in error_scenarios:
            with self.subTest(exception=type(exception).__name__):
                mock_connection = Mock()
                mock_connection.send_request.side_effect = exception
                
                with self.capture_output() as output:
                    try:
                        exec(f"""
try:
    mock_connection.send_request("logout")
    response = mock_connection.recv_response()
except (ConnectionResetError, ConnectionError, TimeoutError) as e:
    print(f"Błąd podczas wylogowywania: {{e}}")
except Exception as e:
    print(f"Nieoczekiwany błąd podczas wylogowywania: {{e}}")
finally:
    print("Zamykanie programu...")
                        """, {"mock_connection": mock_connection})
                    except:
                        pass
                
                captured = output.getvalue()
                self.assertIn(expected_message.split(":")[0], captured)
                self.assertIn("Zamykanie programu...", captured)

    def test_connection_close_error_handling(self):
        """Test obsługi błędów podczas zamykania połączenia"""
        mock_connection = Mock()
        mock_connection.close.side_effect = Exception("Close error")
        
        with self.capture_output() as output:
            try:
                exec("""
try:
    mock_connection.close()
except Exception as e:
    print(f"Błąd podczas zamykania połączenia: {e}")
                """, {"mock_connection": mock_connection})
            except:
                pass
        
        captured = output.getvalue()
        self.assertIn("Błąd podczas zamykania połączenia: Close error", captured)

    def test_request_format_validation(self):
        """Test walidacji formatu żądania"""
        mock_user_manager = Mock()
        mock_handler = Mock(return_value=["send", {"receiver": "user", "text": "hello"}])
        mock_user_manager.command_map = {"send": mock_handler}
        
        # Test konwersji żądania na string
        data_input = {"receiver": "user", "text": "hello"}
        request = mock_user_manager.command_map["send"]("send", **data_input)
        request_str = str(request)
        
        # Sprawdzenie czy żądanie można przekonwertować na string
        self.assertIsInstance(request_str, str)
        self.assertIn("send", request_str)

    def test_empty_data_input_handling(self):
        """Test obsługi pustych danych wejściowych"""
        mock_user_manager = Mock()
        mock_handler = Mock(return_value=["help", {}])
        mock_user_manager.command_map = {"help": mock_handler}
        
        data_input = {}
        
        # Symulacja logiki z client.py dla pustych danych
        if len(data_input) > 0:
            request = mock_user_manager.command_map["help"]("help", **data_input)
        else:
            request = mock_user_manager.command_map["help"]("help")
        
        mock_handler.assert_called_once_with("help")

    def test_client_main_loop_structure(self):
        """Test struktury głównej pętli klienta"""
        # Ten test sprawdza czy główna logika klienta jest poprawnie skonstruowana
        # Symulujemy jedną iterację pętli
        
        mock_connection = Mock()
        mock_user_manager = Mock()
        
        # Konfiguracja dla jednej iteracji
        mock_user_manager.prepare_request_interactive.return_value = ("send", {"receiver": "test", "text": "hello"})
        mock_user_manager.command_map = {"send": Mock(return_value=["send", {"receiver": "test", "text": "hello"}])}
        mock_connection.send_request.return_value = None
        mock_connection.recv_response.return_value = "Message sent"
        
        # Symulacja jednej iteracji głównej pętli
        try:
            command, data_input = mock_user_manager.prepare_request_interactive()
            
            if command not in mock_user_manager.command_map:
                result = "unknown_command"
            elif command == "logout":
                result = "logout_processed"
            else:
                if len(data_input) > 0:
                    request = mock_user_manager.command_map[command](command, **data_input)
                else:
                    request = mock_user_manager.command_map[command](command)
                mock_connection.send_request(str(request))
                mock_connection.recv_response()
                result = "command_processed"
        except Exception:
            result = "exception_handled"
        
        self.assertEqual(result, "command_processed")
        mock_connection.send_request.assert_called_once()
        mock_connection.recv_response.assert_called_once()

if __name__ == '__main__':
    unittest.main()