import unittest
import socket
from unittest.mock import patch, MagicMock
from BLL.ClientConnectionManager import ClientConnectionManager

class TestClientConnectionManager(unittest.TestCase):
    def setUp(self):
        self.host = "localhost"
        self.port = 12345
        self.manager = ClientConnectionManager()
        self.manager.host = self.host
        self.manager.port = self.port

    @patch('BLL.ClientConnectionManager.s.socket')
    def test_connection_establishment(self, mock_socket):
        # Konfiguracja mocka
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Test nawiązywania połączenia
        with self.manager as manager:
            mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
            mock_socket_instance.connect.assert_called_once_with((self.host, self.port))
            mock_socket_instance.settimeout.assert_called_once()

    @patch('BLL.ClientConnectionManager.s.socket')
    @patch('BLL.ClientConnectionManager.time.sleep')  # Mock sleep aby przyspieszyć testy
    def test_connection_refused_error(self, mock_sleep, mock_socket):
        # Symulacja błędu połączenia
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.connect.side_effect = ConnectionRefusedError("Connection refused")

        # Test obsługi błędu połączenia - oczekujemy ConnectionError po wyczerpaniu prób
        with self.assertRaises(ConnectionError) as context:
            with self.manager:
                pass
        
        # Sprawdzenie czy błąd zawiera informację o pierwotnym wyjątku
        self.assertIn("Connection refused", str(context.exception))

    @patch('BLL.ClientConnectionManager.s.socket')
    def test_send_request(self, mock_socket):
        # Konfiguracja mocka
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        test_command = "test command"

        # Test wysyłania komendy
        with self.manager as manager:
            manager.send_request(test_command)
            mock_socket_instance.send.assert_called_once_with(test_command.encode("utf-8"))

    @patch('BLL.ClientConnectionManager.s.socket')
    def test_recv_response(self, mock_socket):
        # Konfiguracja mocka
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        test_response = "test response"
        mock_socket_instance.recv.return_value = test_response.encode("utf-8")

        # Test odbierania odpowiedzi
        with self.manager as manager:
            response = manager.recv_response()
            self.assertEqual(response, test_response)
            # Sprawdzenie czy recv został wywołany z buffer_size z config
            mock_socket_instance.recv.assert_called_once()

    @patch('BLL.ClientConnectionManager.s.socket')
    def test_connection_reset_error(self, mock_socket):
        # Konfiguracja mocka
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.recv.side_effect = ConnectionResetError("Connection reset")

        # Test obsługi błędu resetu połączenia - oczekujemy ConnectionError
        with self.manager as manager:
            with self.assertRaises(ConnectionError) as context:
                manager.recv_response()
            
            # Sprawdzenie czy błąd zawiera informację o pierwotnym wyjątku
            self.assertIn("Connection reset", str(context.exception))

    @patch('BLL.ClientConnectionManager.s.socket')
    def test_connection_close(self, mock_socket):
        # Konfiguracja mocka
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance

        # Test zamykania połączenia
        with self.manager:
            pass
        mock_socket_instance.close.assert_called_once()

    @patch('BLL.ClientConnectionManager.s.socket')
    @patch('BLL.ClientConnectionManager.time.sleep')
    def test_retry_mechanism_success_on_second_attempt(self, mock_sleep, mock_socket):
        """Test mechanizmu retry - sukces przy drugiej próbie"""
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        
        # Pierwsza próba kończy się błędem, druga sukcesem
        mock_socket_instance.connect.side_effect = [
            ConnectionRefusedError("First attempt failed"),
            None  # Druga próba jest udana
        ]
        
        with self.manager as manager:
            # Sprawdzenie czy connect został wywołany dwukrotnie
            self.assertEqual(mock_socket_instance.connect.call_count, 2)
            # Sprawdzenie czy sleep został wywołany raz (między próbami)
            mock_sleep.assert_called_once_with(1.0)  # RETRY_DELAY

    @patch('BLL.ClientConnectionManager.s.socket')
    def test_send_request_validation(self, mock_socket):
        """Test walidacji danych przed wysłaniem"""
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        
        with self.manager as manager:
            # Test pustej komendy
            with self.assertRaises(ValueError) as context:
                manager.send_request("")
            self.assertIn("nie może być pusta", str(context.exception))
            
            # Test komendy zawierającej tylko białe znaki
            with self.assertRaises(ValueError) as context:
                manager.send_request("   ")
            self.assertIn("nie może być pusta", str(context.exception))

    @patch('BLL.ClientConnectionManager.s.socket')
    def test_send_request_max_size_validation(self, mock_socket):
        """Test walidacji maksymalnego rozmiaru komendy"""
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        
        with self.manager as manager:
            # Komenda przekraczająca maksymalny rozmiar (MAX_REQUEST_SIZE = 2048)
            large_command = "x" * 3000
            with self.assertRaises(ValueError) as context:
                manager.send_request(large_command)
            self.assertIn("przekracza maksymalny rozmiar", str(context.exception))

    @patch('BLL.ClientConnectionManager.s.socket')
    def test_send_request_without_connection(self, mock_socket):
        """Test wysyłania bez aktywnego połączenia"""
        # Nie używamy context managera, więc nie ma aktywnego połączenia
        with self.assertRaises(ConnectionError) as context:
            self.manager.send_request("test")
        self.assertIn("Brak aktywnego połączenia", str(context.exception))

    @patch('BLL.ClientConnectionManager.s.socket')
    def test_recv_response_without_connection(self, mock_socket):
        """Test odbierania bez aktywnego połączenia"""
        # Nie używamy context managera, więc nie ma aktywnego połączenia
        with self.assertRaises(ConnectionError) as context:
            self.manager.recv_response()
        self.assertIn("Brak aktywnego połączenia", str(context.exception))

    @patch('BLL.ClientConnectionManager.s.socket')
    def test_recv_response_empty_response(self, mock_socket):
        """Test obsługi pustej odpowiedzi (serwer zamknął połączenie)"""
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        mock_socket_instance.recv.return_value = b""  # Pusta odpowiedź
        
        with self.manager as manager:
            with self.assertRaises(ConnectionError) as context:
                manager.recv_response()
            self.assertIn("Serwer zamknął połączenie", str(context.exception))

    @patch('BLL.ClientConnectionManager.s.socket')
    def test_recv_response_unicode_decode_error(self, mock_socket):
        """Test obsługi błędu dekodowania Unicode"""
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        # Nieprawidłowe dane Unicode
        mock_socket_instance.recv.return_value = b'\xff\xfe'
        
        with self.manager as manager:
            with self.assertRaises(ValueError) as context:
                manager.recv_response()
            self.assertIn("Nieprawidłowe kodowanie", str(context.exception))

    @patch('BLL.ClientConnectionManager.s.socket')
    def test_send_request_network_errors(self, mock_socket):
        """Test obsługi różnych błędów sieciowych podczas wysyłania"""
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        
        test_cases = [
            (ConnectionResetError("Reset"), "Połączenie przerwane"),
            (ConnectionAbortedError("Aborted"), "Połączenie przerwane"),
            (BrokenPipeError("Broken pipe"), "Połączenie przerwane"),
        ]
        
        for error, expected_msg in test_cases:
            with self.subTest(error=error.__class__.__name__):
                mock_socket_instance.send.side_effect = error
                
                with self.manager as manager:
                    with self.assertRaises(ConnectionError) as context:
                        manager.send_request("test")
                    self.assertIn(expected_msg, str(context.exception))

    @patch('BLL.ClientConnectionManager.s.socket')
    def test_timeout_handling(self, mock_socket):
        """Test obsługi timeout'ów"""
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        
        # Test timeout podczas wysyłania
        import socket as sock_module
        mock_socket_instance.send.side_effect = sock_module.timeout("Send timeout")
        
        with self.manager as manager:
            with self.assertRaises(TimeoutError) as context:
                manager.send_request("test")
            self.assertIn("Timeout podczas wysyłania", str(context.exception))

    def test_close_method(self):
        """Test metody close()"""
        # Symulacja istniejącego socketu
        mock_socket = MagicMock()
        self.manager.client_socket = mock_socket
        
        # Test zamknięcia
        self.manager.close()
        mock_socket.close.assert_called_once()

    def test_close_method_no_socket(self):
        """Test metody close() gdy nie ma socketu"""
        # Test gdy nie ma socketu - nie powinno rzucać błędu
        self.manager.close()
        # Test przeszedł jeśli nie było wyjątku

if __name__ == '__main__':
    unittest.main() 