import unittest
import uuid
import re
from datetime import datetime
from unittest.mock import patch, MagicMock
from Models.message import Message

class TestMessage(unittest.TestCase):
    
    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem"""
        self.message = Message()

    def test_message_constructor_default_values(self):
        """Test domyślnych wartości konstruktora Message"""
        message = Message()
        
        self.assertIsNone(message.id)
        self.assertIsNone(message.username)
        self.assertIsNone(message.sender)
        self.assertIsNone(message.text)
        self.assertIsNotNone(message.send_time)
        self.assertIsNone(message.read_time)
        self.assertEqual(message.is_read, 0)

    def test_message_send_time_format(self):
        """Test formatu send_time w konstruktorze"""
        message = Message()
        
        # Sprawdzenie czy send_time ma poprawny format
        time_pattern = r'\d{4}-\d{2}-\d{2} godz\. \d{2}:\d{2}'
        self.assertIsNotNone(re.match(time_pattern, message.send_time))

    def test_message_attributes_assignment(self):
        """Test przypisywania wartości do atrybutów Message"""
        message = Message()
        
        message.id = "test_id_123"
        message.username = "test_user"
        message.sender = "test_sender"
        message.text = "Test message content"
        message.read_time = "2024-01-01 godz. 12:00"
        message.is_read = 1
        
        self.assertEqual(message.id, "test_id_123")
        self.assertEqual(message.username, "test_user")
        self.assertEqual(message.sender, "test_sender")
        self.assertEqual(message.text, "Test message content")
        self.assertEqual(message.read_time, "2024-01-01 godz. 12:00")
        self.assertEqual(message.is_read, 1)

    def test_generate_id_uuid_format(self):
        """Test generowania UUID ID"""
        generated_id = self.message._generate_id()
        
        self.assertIsInstance(generated_id, str)
        # Sprawdzenie czy to prawidłowy UUID
        try:
            uuid.UUID(generated_id)
            is_valid_uuid = True
        except ValueError:
            is_valid_uuid = False
        
        self.assertTrue(is_valid_uuid)

    def test_generate_id_uniqueness(self):
        """Test unikalności generowanych UUID ID"""
        ids = set()
        for _ in range(100):
            new_id = self.message._generate_id()
            self.assertNotIn(new_id, ids)
            ids.add(new_id)

    @patch('time.time')
    @patch('secrets.randbits')
    def test_generate_numeric_id(self, mock_randbits, mock_time):
        """Test generowania numerycznego ID"""
        mock_time.return_value = 1640995200.0  # 2022-01-01 00:00:00
        mock_randbits.return_value = 123
        
        numeric_id = self.message._generate_numeric_id()
        
        self.assertIsInstance(numeric_id, int)
        self.assertGreater(numeric_id, 0)
        mock_randbits.assert_called_once()

    def test_generate_numeric_id_uniqueness(self):
        """Test unikalności generowanych numerycznych ID"""
        ids = set()
        for _ in range(100):
            new_id = self.message._generate_numeric_id()
            self.assertNotIn(new_id, ids)
            ids.add(new_id)

    @patch('secrets.token_hex')
    def test_generate_short_id(self, mock_token_hex):
        """Test generowania krótkiego ID"""
        mock_token_hex.return_value = "a1b2c3d4"
        
        short_id = self.message._generate_short_id()
        
        self.assertEqual(short_id, "a1b2c3d4")
        mock_token_hex.assert_called_once()

    def test_generate_short_id_format(self):
        """Test formatu krótkiego ID"""
        short_id = self.message._generate_short_id()
        
        self.assertIsInstance(short_id, str)
        # Sprawdzenie czy to prawidłowy hex string
        hex_pattern = r'^[a-f0-9]+$'
        self.assertIsNotNone(re.match(hex_pattern, short_id))

    def test_generate_short_id_uniqueness(self):
        """Test unikalności generowanych krótkich ID"""
        ids = set()
        for _ in range(100):
            new_id = self.message._generate_short_id()
            self.assertNotIn(new_id, ids)
            ids.add(new_id)

    @patch('Models.message.datetime')
    def test_generate_send_time(self, mock_datetime):
        """Test generowania send_time"""
        mock_now = MagicMock()
        mock_now.strftime.return_value = "2024-01-01 godz. 12:00"
        mock_datetime.now.return_value = mock_now
        
        send_time = self.message._generate_send_time()
        
        self.assertEqual(send_time, "2024-01-01 godz. 12:00")
        mock_datetime.now.assert_called_once()
        mock_now.strftime.assert_called_once_with('%Y-%m-%d godz. %H:%M')

    @patch('Models.message.datetime')
    def test_generate_read_time(self, mock_datetime):
        """Test generowania read_time"""
        mock_now = MagicMock()
        mock_now.strftime.return_value = "2024-01-01 godz. 12:30"
        mock_datetime.now.return_value = mock_now
        
        read_time = self.message._generate_read_time()
        
        self.assertEqual(read_time, "2024-01-01 godz. 12:30")
        mock_datetime.now.assert_called_once()
        mock_now.strftime.assert_called_once_with('%Y-%m-%d godz. %H:%M')

    def test_generate_send_time_format(self):
        """Test rzeczywistego formatu generate_send_time"""
        send_time = self.message._generate_send_time()
        
        time_pattern = r'\d{4}-\d{2}-\d{2} godz\. \d{2}:\d{2}'
        self.assertIsNotNone(re.match(time_pattern, send_time))

    def test_generate_read_time_format(self):
        """Test rzeczywistego formatu generate_read_time"""
        read_time = self.message._generate_read_time()
        
        time_pattern = r'\d{4}-\d{2}-\d{2} godz\. \d{2}:\d{2}'
        self.assertIsNotNone(re.match(time_pattern, read_time))

    def test_message_state_changes(self):
        """Test zmiany stanu wiadomości z nieprzeczytanej na przeczytaną"""
        message = Message()
        
        # Początkowy stan - nieprzeczytana
        self.assertEqual(message.is_read, 0)
        self.assertIsNone(message.read_time)
        
        # Zmiana na przeczytaną
        message.is_read = 1
        message.read_time = message._generate_read_time()
        
        self.assertEqual(message.is_read, 1)
        self.assertIsNotNone(message.read_time)

    def test_message_complete_workflow(self):
        """Test kompletnego workflow wiadomości"""
        message = Message()
        
        # Ustawienie wszystkich wymaganych pól
        message.id = message._generate_id()
        message.username = "recipient"
        message.sender = "sender"
        message.text = "Hello, this is a test message!"
        
        # Sprawdzenie że wiadomość jest gotowa do wysłania
        self.assertIsNotNone(message.id)
        self.assertIsNotNone(message.username)
        self.assertIsNotNone(message.sender)
        self.assertIsNotNone(message.text)
        self.assertIsNotNone(message.send_time)
        self.assertEqual(message.is_read, 0)
        self.assertIsNone(message.read_time)
        
        # Symulacja przeczytania wiadomości
        message.is_read = 1
        message.read_time = message._generate_read_time()
        
        self.assertEqual(message.is_read, 1)
        self.assertIsNotNone(message.read_time)

    def test_message_data_types(self):
        """Test typów danych atrybutów Message"""
        message = Message()
        
        message.id = "string_id"
        message.username = "username"
        message.sender = "sender"
        message.text = "message text"
        message.send_time = "2024-01-01 godz. 12:00"
        message.read_time = "2024-01-01 godz. 12:30"
        message.is_read = 1
        
        self.assertIsInstance(message.id, str)
        self.assertIsInstance(message.username, str)
        self.assertIsInstance(message.sender, str)
        self.assertIsInstance(message.text, str)
        self.assertIsInstance(message.send_time, str)
        self.assertIsInstance(message.read_time, str)
        self.assertIsInstance(message.is_read, int)

    def test_message_empty_values(self):
        """Test obsługi pustych wartości"""
        message = Message()
        
        message.id = ""
        message.username = ""
        message.sender = ""
        message.text = ""
        
        self.assertEqual(message.id, "")
        self.assertEqual(message.username, "")
        self.assertEqual(message.sender, "")
        self.assertEqual(message.text, "")

if __name__ == '__main__':
    unittest.main()