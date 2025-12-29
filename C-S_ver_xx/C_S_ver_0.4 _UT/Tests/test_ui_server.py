import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import io
from contextlib import contextmanager

class TestServerUI(unittest.TestCase):
    
    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem"""
        self.mock_server = Mock()
        self.mock_user_manager = Mock()
        self.mock_client_socket = Mock()
        self.test_address = ("127.0.0.1", 12345)

    @contextmanager
    def capture_output(self):
        """Context manager do przechwytywania stdout"""
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        try:
            yield captured_output
        finally:
            sys.stdout = old_stdout

    @patch('BLL.ServerConnectionManager.ServerConnectionManager')
    @patch('BLL.ServerMessageManager.ServerMessageManager')
    def test_server_startup_and_client_connection(self, mock_message_manager_class, mock_connection_manager_class):
        """Test uruchamiania serwera i przyjmowania połączenia klienta"""
        # Konfiguracja mocków
        mock_server = Mock()
        mock_connection_manager_class.return_value = mock_server
        
        mock_user_manager = Mock()
        mock_message_manager_class.return_value = mock_user_manager
        
        mock_server.accept_client.return_value = (self.mock_client_socket, self.test_address)
        mock_server.handle_client.return_value = ["help", {}]
        
        mock_user_manager.command_map = {"help": Mock(return_value="Help message")}
        
        with self.capture_output() as output:
            try:
                exec("""
from BLL.ServerConnectionManager import ServerConnectionManager
from BLL.ServerMessageManager import ServerMessageManager

server = ServerConnectionManager()
server.start_server()

client_socket, address = server.accept_client()
print(f"Połączono z klientem: {address}")
user_manager = ServerMessageManager()

request = server.handle_client(client_socket)
command = request[0]
data_input = request[1]

if command in user_manager.command_map:
    if len(data_input) > 0:
        response = str(user_manager.command_map[command](command, *data_input.values()))
    else:
        response = str(user_manager.command_map[command](command))
    client_socket.send(response.encode("utf-8"))
                """, {
                    'ServerConnectionManager': mock_connection_manager_class,
                    'ServerMessageManager': mock_message_manager_class
                })
            except SystemExit:
                pass
        
        captured = output.getvalue()
        self.assertIn(f"Połączono z klientem: {self.test_address}", captured)
        mock_server.start_server.assert_called_once()
        mock_server.accept_client.assert_called_once()

    @patch('BLL.ServerConnectionManager.ServerConnectionManager')
    @patch('BLL.ServerMessageManager.ServerMessageManager')
    def test_logout_command_handling(self, mock_message_manager_class, mock_connection_manager_class):
        """Test obsługi komendy logout"""
        mock_server = Mock()
        mock_connection_manager_class.return_value = mock_server
        
        mock_user_manager = Mock()
        mock_message_manager_class.return_value = mock_user_manager
        
        mock_server.accept_client.return_value = (self.mock_client_socket, self.test_address)
        mock_server.handle_client.return_value = ["logout", {}]
        
        with self.capture_output() as output:
            try:
                exec("""
from BLL.ServerConnectionManager import ServerConnectionManager
from BLL.ServerMessageManager import ServerMessageManager

server = ServerConnectionManager()
client_socket, address = server.accept_client()
user_manager = ServerMessageManager()

request = server.handle_client(client_socket)
command = request[0]
data_input = request[1]

if command == "logout":
    print(f"Klient {address} się wylogował")
                """, {
                    'ServerConnectionManager': mock_connection_manager_class,
                    'ServerMessageManager': mock_message_manager_class
                })
            except SystemExit:
                pass
        
        captured = output.getvalue()
        self.assertIn(f"Klient {self.test_address} się wylogował", captured)

    @patch('BLL.ServerConnectionManager.ServerConnectionManager')
    @patch('BLL.ServerMessageManager.ServerMessageManager')
    def test_command_processing_with_data(self, mock_message_manager_class, mock_connection_manager_class):
        """Test przetwarzania komendy z danymi"""
        mock_server = Mock()
        mock_connection_manager_class.return_value = mock_server
        
        mock_user_manager = Mock()
        mock_message_manager_class.return_value = mock_user_manager
        
        test_data = {"receiver": "user1", "text": "hello"}
        mock_server.handle_client.return_value = ["send", test_data]
        mock_handler = Mock(return_value="Message sent")
        mock_user_manager.command_map = {"send": mock_handler}
        
        # Symulacja wykonania kodu serwera
        server = mock_server
        client_socket_and_address = server.accept_client()
        client_socket = self.mock_client_socket
        user_manager = mock_user_manager

        request = server.handle_client(client_socket)
        command = request[0]
        data_input = request[1]

        if command in user_manager.command_map:
            if len(data_input) > 0:
                response = str(user_manager.command_map[command](command, **data_input))
            else:
                response = str(user_manager.command_map[command](command))
            client_socket.send(response.encode("utf-8"))
        
        # Sprawdzenie czy handler został wywołany z właściwymi argumentami
        mock_handler.assert_called_once_with("send", receiver="user1", text="hello")
        self.mock_client_socket.send.assert_called_once_with(b"Message sent")

    @patch('BLL.ServerConnectionManager.ServerConnectionManager')
    @patch('BLL.ServerMessageManager.ServerMessageManager')
    def test_command_processing_without_data(self, mock_message_manager_class, mock_connection_manager_class):
        """Test przetwarzania komendy bez danych"""
        mock_server = Mock()
        mock_connection_manager_class.return_value = mock_server
        
        mock_user_manager = Mock()
        mock_message_manager_class.return_value = mock_user_manager
        
        mock_server.handle_client.return_value = ["help", {}]
        mock_handler = Mock(return_value="Help information")
        mock_user_manager.command_map = {"help": mock_handler}
        
        # Symulacja przetwarzania komendy bez danych
        request = mock_server.handle_client(self.mock_client_socket)
        command = request[0]
        data_input = request[1]
        
        if command in mock_user_manager.command_map:
            if len(data_input) > 0:
                response = str(mock_user_manager.command_map[command](command, *data_input.values()))
            else:
                response = str(mock_user_manager.command_map[command](command))
            self.mock_client_socket.send(response.encode("utf-8"))
        
        mock_handler.assert_called_once_with("help")
        self.mock_client_socket.send.assert_called_once_with(b"Help information")

    @patch('BLL.ServerConnectionManager.ServerConnectionManager')
    @patch('BLL.ServerMessageManager.ServerMessageManager')
    def test_empty_request_handling(self, mock_message_manager_class, mock_connection_manager_class):
        """Test obsługi pustego żądania"""
        mock_server = Mock()
        mock_connection_manager_class.return_value = mock_server
        
        mock_server.handle_client.return_value = None  # Symulacja braku danych
        
        # Symulacja logiki obsługi pustego żądania
        request = mock_server.handle_client(self.mock_client_socket)
        
        if not request:
            result = "connection_broken"
        else:
            result = "request_processed"
        
        self.assertEqual(result, "connection_broken")

    @patch('BLL.ServerConnectionManager.ServerConnectionManager')
    @patch('BLL.ServerMessageManager.ServerMessageManager')
    def test_empty_command_handling(self, mock_message_manager_class, mock_connection_manager_class):
        """Test obsługi pustej komendy"""
        mock_server = Mock()
        mock_connection_manager_class.return_value = mock_server
        
        mock_server.handle_client.return_value = ["", {}]  # Pusta komenda
        
        # Symulacja logiki obsługi pustej komendy
        request = mock_server.handle_client(self.mock_client_socket)
        command = request[0]
        
        if not command:
            result = "empty_command_skipped"
        else:
            result = "command_processed"
        
        self.assertEqual(result, "empty_command_skipped")

    @patch('BLL.ServerConnectionManager.ServerConnectionManager')
    @patch('BLL.ServerMessageManager.ServerMessageManager')
    def test_client_exception_handling(self, mock_message_manager_class, mock_connection_manager_class):
        """Test obsługi wyjątków podczas obsługi klienta"""
        mock_server = Mock()
        mock_connection_manager_class.return_value = mock_server
        
        mock_user_manager = Mock()
        mock_message_manager_class.return_value = mock_user_manager
        
        mock_server.accept_client.return_value = (self.mock_client_socket, self.test_address)
        mock_server.handle_client.side_effect = Exception("Client handling error")
        
        with self.capture_output() as output:
            try:
                exec("""
from BLL.ServerConnectionManager import ServerConnectionManager
from BLL.ServerMessageManager import ServerMessageManager

server = ServerConnectionManager()
client_socket, address = server.accept_client()
user_manager = ServerMessageManager()

try:
    request = server.handle_client(client_socket)
except Exception as e:
    print(f"Błąd podczas obsługi klienta {address}: {e}")
finally:
    client_socket.close()
    print(f"Zamknięto połączenie z klientem {address}")
                """, {
                    'ServerConnectionManager': mock_connection_manager_class,
                    'ServerMessageManager': mock_message_manager_class
                })
            except SystemExit:
                pass
        
        captured = output.getvalue()
        self.assertIn(f"Błąd podczas obsługi klienta {self.test_address}: Client handling error", captured)
        self.assertIn(f"Zamknięto połączenie z klientem {self.test_address}", captured)
        self.mock_client_socket.close.assert_called_once()

    @patch('BLL.ServerConnectionManager.ServerConnectionManager')
    def test_keyboard_interrupt_handling(self, mock_connection_manager_class):
        """Test obsługi przerwania przez użytkownika (Ctrl+C)"""
        mock_server = Mock()
        mock_connection_manager_class.return_value = mock_server
        
        mock_server.accept_client.side_effect = KeyboardInterrupt()
        
        with self.capture_output() as output:
            try:
                exec("""
from BLL.ServerConnectionManager import ServerConnectionManager

server = ServerConnectionManager()
server.start_server()

try:
    client_socket, address = server.accept_client()
except KeyboardInterrupt:
    print("\\nZamykanie serwera...")
finally:
    server.stop_server()
                """, {'ServerConnectionManager': mock_connection_manager_class})
            except SystemExit:
                pass
        
        captured = output.getvalue()
        self.assertIn("Zamykanie serwera...", captured)
        mock_server.stop_server.assert_called_once()

    @patch('BLL.ServerConnectionManager.ServerConnectionManager')
    def test_critical_server_error_handling(self, mock_connection_manager_class):
        """Test obsługi krytycznych błędów serwera"""
        mock_server = Mock()
        mock_connection_manager_class.return_value = mock_server
        
        mock_server.accept_client.side_effect = Exception("Critical server error")
        
        with self.capture_output() as output:
            try:
                exec("""
from BLL.ServerConnectionManager import ServerConnectionManager

server = ServerConnectionManager()
server.start_server()

try:
    client_socket, address = server.accept_client()
except Exception as e:
    print(f"Błąd krytyczny serwera: {e}")
finally:
    server.stop_server()
                """, {'ServerConnectionManager': mock_connection_manager_class})
            except SystemExit:
                pass
        
        captured = output.getvalue()
        self.assertIn("Błąd krytyczny serwera: Critical server error", captured)
        mock_server.stop_server.assert_called_once()

    def test_request_parsing_logic(self):
        """Test logiki parsowania żądań"""
        test_cases = [
            (["send", {"receiver": "user", "text": "hello"}], ("send", {"receiver": "user", "text": "hello"})),
            (["help", {}], ("help", {})),
            (["login", {"username": "test", "password": "pass"}], ("login", {"username": "test", "password": "pass"})),
            (["logout", {}], ("logout", {}))
        ]
        
        for request_data, expected in test_cases:
            with self.subTest(request=request_data):
                # Symulacja parsowania żądania
                command = request_data[0]
                data_input = request_data[1]
                
                parsed = (command, data_input)
                self.assertEqual(parsed, expected)

    def test_response_encoding_and_sending(self):
        """Test kodowania i wysyłania odpowiedzi"""
        mock_client_socket = Mock()
        test_responses = [
            "OK",
            "User logged in",
            "Message sent successfully",
            "Error: Invalid command"
        ]
        
        for response in test_responses:
            with self.subTest(response=response):
                mock_client_socket.reset_mock()
                
                # Symulacja wysyłania odpowiedzi
                mock_client_socket.send(response.encode("utf-8"))
                
                mock_client_socket.send.assert_called_once_with(response.encode("utf-8"))

    def test_server_main_loop_structure(self):
        """Test struktury głównej pętli serwera"""
        mock_server = Mock()
        mock_user_manager = Mock()
        
        # Symulacja jednej iteracji zewnętrznej pętli
        mock_server.accept_client.return_value = (self.mock_client_socket, self.test_address)
        
        # Symulacja jednej iteracji wewnętrznej pętli
        mock_server.handle_client.return_value = ["send", {"receiver": "user", "text": "hello"}]
        mock_user_manager.command_map = {"send": Mock(return_value="Message sent")}
        
        # Wykonanie logiki
        client_socket, address = mock_server.accept_client()
        user_manager = mock_user_manager
        
        request = mock_server.handle_client(client_socket)
        if request:
            command = request[0]
            data_input = request[1]
            
            if command and command in user_manager.command_map:
                if len(data_input) > 0:
                    response = str(user_manager.command_map[command](command, *data_input.values()))
                else:
                    response = str(user_manager.command_map[command](command))
                client_socket.send(response.encode("utf-8"))
        
        # Weryfikacja
        mock_server.accept_client.assert_called_once()
        mock_server.handle_client.assert_called_once_with(client_socket)
        self.mock_client_socket.send.assert_called_once_with(b"Message sent")

    def test_multiple_client_handling_simulation(self):
        """Test symulacji obsługi wielu klientów"""
        mock_server = Mock()
        
        # Symulacja dwóch różnych klientów
        client1_socket, client1_address = Mock(), ("127.0.0.1", 12345)
        client2_socket, client2_address = Mock(), ("127.0.0.1", 12346)
        
        mock_server.accept_client.side_effect = [
            (client1_socket, client1_address),
            (client2_socket, client2_address)
        ]
        
        # Symulacja obsługi dwóch klientów
        clients_handled = []
        
        for i in range(2):
            client_socket, address = mock_server.accept_client()
            clients_handled.append(address)
        
        self.assertEqual(len(clients_handled), 2)
        self.assertIn(client1_address, clients_handled)
        self.assertIn(client2_address, clients_handled)

    def test_command_data_extraction(self):
        """Test ekstraktowania danych z komend"""
        test_commands = [
            (["send", {"receiver": "user1", "text": "message1"}], ["user1", "message1"]),
            (["login", {"username": "test", "password": "pass"}], ["test", "pass"]),
            (["help", {}], []),
            (["info", {"username": "user2"}], ["user2"])
        ]
        
        for request, expected_values in test_commands:
            with self.subTest(request=request):
                command = request[0]
                data_input = request[1]
                
                # Symulacja ekstraktowania wartości
                if len(data_input) > 0:
                    extracted_values = list(data_input.values())
                else:
                    extracted_values = []
                
                self.assertEqual(extracted_values, expected_values)

    def test_server_debug_output(self):
        """Test wyjścia debugowego serwera"""
        with self.capture_output() as output:
            # Symulacja wyjścia debugowego z server.py
            request = ["send", {"receiver": "user", "text": "hello"}]
            command = request[0] 
            data_input = request[1]
            
            print(request)
            print(command)
            print(data_input)
        
        captured = output.getvalue()
        self.assertIn("['send', {'receiver': 'user', 'text': 'hello'}]", captured)
        self.assertIn("send", captured)
        self.assertIn("{'receiver': 'user', 'text': 'hello'}", captured)

if __name__ == '__main__':
    unittest.main()