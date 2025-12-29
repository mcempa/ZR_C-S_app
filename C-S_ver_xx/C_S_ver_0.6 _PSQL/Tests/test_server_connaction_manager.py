import unittest
from unittest.mock import Mock, patch
import socket
import ast
from BLL.ServerConnectionManager import ServerConnectionManager
from config import SERVER_CONFIG

class TestServerConnectionManager(unittest.TestCase):
    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem"""
        self.server_manager = ServerConnectionManager()

    def tearDown(self):
        """Czyszczenie po każdym teście"""
        if self.server_manager.server_socket:
            self.server_manager.stop_server()

    def test_init(self):
        """Test inicjalizacji ServerConnectionManager"""
        self.assertEqual(self.server_manager.host, SERVER_CONFIG["host"])
        self.assertEqual(self.server_manager.port, SERVER_CONFIG["port"])
        self.assertEqual(self.server_manager.max_connections, SERVER_CONFIG["max_connections"])
        self.assertEqual(self.server_manager.buffer_size, SERVER_CONFIG["buffer_size"])
        self.assertIsNone(self.server_manager.server_socket)

    @patch('socket.socket')
    def test_start_server_success(self, mock_socket):
        """Test poprawnego uruchomienia serwera"""
        # Przygotowanie mocka
        mock_socket_instance = Mock()
        mock_socket.return_value = mock_socket_instance

        # Wywołanie testowanej metody
        self.server_manager.start_server()

        # Sprawdzenie czy socket został poprawnie skonfigurowany
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_socket_instance.bind.assert_called_once_with(
            (SERVER_CONFIG["host"], SERVER_CONFIG["port"])
        )
        mock_socket_instance.listen.assert_called_once_with(
            SERVER_CONFIG["max_connections"]
        )

    @patch('socket.socket')
    def test_start_server_error(self, mock_socket):
        """Test obsługi błędu podczas uruchamiania serwera"""
        # Symulacja błędu podczas bind
        mock_socket_instance = Mock()
        mock_socket_instance.bind.side_effect = socket.error("Test error")
        mock_socket.return_value = mock_socket_instance

        # Sprawdzenie czy błąd jest odpowiednio obsługiwany
        with self.assertRaises(socket.error) as context:
            self.server_manager.start_server()
        self.assertEqual(str(context.exception), "Nie można uruchomić serwera: Test error")

    def test_stop_server(self):
        """Test zatrzymania serwera"""
        # Przygotowanie mocka
        mock_socket = Mock()
        self.server_manager.server_socket = mock_socket

        # Wywołanie testowanej metody
        self.server_manager.stop_server()

        # Sprawdzenie czy socket został zamknięty
        mock_socket.close.assert_called_once()

    def test_accept_client_success(self):
        """Test poprawnego akceptowania klienta"""
        # Przygotowanie mocka
        mock_socket = Mock()
        mock_client = Mock()
        mock_address = ('127.0.0.1', 12345)
        mock_socket.accept.return_value = (mock_client, mock_address)
        self.server_manager.server_socket = mock_socket

        # Wywołanie testowanej metody
        client, address = self.server_manager.accept_client()

        # Sprawdzenie wyników
        self.assertEqual(client, mock_client)
        self.assertEqual(address, mock_address)
        mock_socket.accept.assert_called_once()

    def test_accept_client_error(self):
        """Test obsługi błędu podczas akceptowania klienta"""
        # Przygotowanie mocka
        mock_socket = Mock()
        mock_socket.accept.side_effect = socket.error("Accept error")
        self.server_manager.server_socket = mock_socket

        # Sprawdzenie czy błąd jest odpowiednio obsługiwany
        with self.assertRaises(socket.error) as context:
            self.server_manager.accept_client()
        self.assertEqual(str(context.exception), "Błąd akceptowania: Accept error")

    def test_handle_client_success(self):
        """Test poprawnego obsługiwania danych od klienta"""
        # Przygotowanie mocka klienta
        mock_client = Mock()
        test_data = ["test", {"data": 123}]
        mock_client.recv.return_value = '["test", {"data": 123}]'.encode('utf-8')

        # Wywołanie testowanej metody
        result = self.server_manager.handle_client(mock_client)

        # Sprawdzenie wyników
        self.assertEqual(result, test_data)
        mock_client.recv.assert_called_once_with(1024)

    def test_handle_client_decode_error(self):
        """Test obsługi błędu dekodowania danych"""
        # Przygotowanie mocka klienta
        mock_client = Mock()
        mock_client.recv.side_effect = UnicodeDecodeError(
            'utf-8', b'invalid', 0, 1, 'Invalid UTF-8'
        )

        # Sprawdzenie czy błąd jest odpowiednio obsługiwany
        with self.assertRaises(UnicodeDecodeError):
            self.server_manager.handle_client(mock_client)

    def test_handle_client_parse_error(self):
        """Test obsługi błędu parsowania danych"""
        # Przygotowanie mocka klienta
        mock_client = Mock()
        mock_client.recv.return_value = "invalid data".encode('utf-8')

        # Sprawdzenie czy błąd jest odpowiednio obsługiwany
        with self.assertRaises((ValueError, SyntaxError)):
            self.server_manager.handle_client(mock_client)

    def test_handle_client_socket_error(self):
        """Test obsługi błędu połączenia"""
        # Przygotowanie mocka klienta
        mock_client = Mock()
        mock_client.recv.side_effect = socket.error("Connection error")

        # Sprawdzenie czy błąd jest odpowiednio obsługiwany
        with self.assertRaises(socket.error) as context:
            self.server_manager.handle_client(mock_client)
        self.assertEqual(str(context.exception), "Connection error")


class TestServerConnectionManagerIntegration(unittest.TestCase):
    """Testy integracyjne dla ServerConnectionManager"""

    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem"""
        self.server = ServerConnectionManager()
        self.server.start_server()
        
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((SERVER_CONFIG["host"], SERVER_CONFIG["port"]))

    def tearDown(self):
        """Czyszczenie po każdym teście"""
        self.client.close()
        self.server.stop_server()

    def test_full_communication(self):
        """Test pełnej komunikacji między serwerem a klientem"""
        # Wysłanie danych
        test_data = ["test", {"data": 123}]
        import json
        self.client.send(json.dumps(test_data).encode('utf-8'))
        
        # Akceptacja klienta przez serwer
        client_socket, _ = self.server.accept_client()
        
        # Odbieranie danych
        received_data = self.server.handle_client(client_socket)
        
        self.assertEqual(received_data, test_data)

    def test_multiple_clients(self):
        """Test obsługi wielu klientów"""
        # Utworzenie drugiego klienta
        client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client2.connect((SERVER_CONFIG["host"], SERVER_CONFIG["port"]))
        
        try:
            # Wysłanie danych od pierwszego klienta
            test_data1 = ["client1", {"data": "test1"}]
            import json
            self.client.send(json.dumps(test_data1).encode('utf-8'))
            
            # Wysłanie danych od drugiego klienta
            test_data2 = ["client2", {"data": "test2"}]
            client2.send(json.dumps(test_data2).encode('utf-8'))
            
            # Akceptacja i obsługa pierwszego klienta
            client_socket1, _ = self.server.accept_client()
            received_data1 = self.server.handle_client(client_socket1)
            
            # Akceptacja i obsługa drugiego klienta
            client_socket2, _ = self.server.accept_client()
            received_data2 = self.server.handle_client(client_socket2)
            
            self.assertEqual(received_data1, test_data1)
            self.assertEqual(received_data2, test_data2)
        finally:
            client2.close()


if __name__ == '__main__':
    unittest.main()
    