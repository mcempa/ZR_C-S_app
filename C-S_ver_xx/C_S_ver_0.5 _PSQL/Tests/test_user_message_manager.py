import unittest
from unittest.mock import Mock, patch
import bcrypt
from datetime import datetime
from BLL.ServerMessageManager import ServerMessageManager
from Models.user import User
from config import *

class TestUserServerManager(unittest.TestCase):
    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem"""
        self.user_manager = ServerMessageManager()
        self.user_manager.db_manager = Mock()  # Mock dla DbManager

    def test_validate_string(self):
        """Test walidacji i sanityzacji tekstu"""
        # Test normalnego tekstu
        self.assertEqual(self.user_manager._validate_string("test"), "test")
        
        # Test z zabronionymi znakami
        self.assertEqual(self.user_manager._validate_string('test"\'{}[];'), "test")
        
        # Test z liczbą
        self.assertEqual(self.user_manager._validate_string(123), "123")
        
        # Test z białymi znakami
        self.assertEqual(self.user_manager._validate_string("  test  "), "test")

    def test_get_help(self):
        """Test wyświetlania pomocy"""
        # Test dla zalogowanego użytkownika
        self.user_manager.current_user.is_logged = True
        self.user_manager.current_user.role = "admin"
        response = self.user_manager.handle_get_help("help")
        self.assertIsInstance(response, str)
        self.assertIn(":", response)

        # Test dla niezalogowanego użytkownika - nadal ma dostęp do pomocy
        self.user_manager.current_user.is_logged = False
        response = self.user_manager.handle_get_help("help")
        self.assertIsInstance(response, str)
        self.assertIn(":", response)

    def test_send_message(self):
        """Test wysyłania wiadomości"""
        # Przygotowanie mocka
        self.user_manager.current_user.is_logged = True
        self.user_manager.current_user.username = "sender"
        self.user_manager.db_manager.is_user_in_db.return_value = True
        self.user_manager.db_manager.get_number_new_message_user.return_value = 0
        self.user_manager.db_manager.add_message_into_db.return_value = True

        # Test poprawnego wysłania wiadomości
        response = self.user_manager.handle_send_message("send", receiver="receiver", text="test message")
        self.assertEqual(response, "Wiadomość do receiver została wysłana")
        
        # Test z nieistniejącym odbiorcą
        self.user_manager.db_manager.is_user_in_db.return_value = False
        response = self.user_manager.handle_send_message("send", receiver="nonexistent", text="test")
        self.assertEqual(response, "Nie masz uprawnień do tej komendy lub użytkownik nonexistent nie istnieje")

    def test_login_user(self):
        """Test logowania użytkownika"""
        # Przygotowanie mocka
        test_password = "test123"
        hashed_password = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
        self.user_manager.db_manager.get_user_password.return_value = hashed_password.decode('utf-8')
        self.user_manager.db_manager.get_user_role.return_value = "user"
        self.user_manager.db_manager.change_login_time_in_db.return_value = True

        # Test poprawnego logowania
        response = self.user_manager.handle_login("login", username="testuser", password=test_password)
        self.assertEqual(response, "Użytkownik został zalogowany")
        self.assertTrue(self.user_manager.current_user.is_logged)
        self.assertEqual(self.user_manager.current_user.username, "testuser")

        # Test z nieprawidłowym hasłem - wyloguj użytkownika przed testem
        self.user_manager.current_user.is_logged = False
        response = self.user_manager.handle_login("login", username="testuser", password="wrongpass")
        self.assertEqual(response, "Nieprawidłowa nazwa użytkownika lub hasło")

    def test_create_new_user(self):
        """Test tworzenia nowego użytkownika"""
        # Przygotowanie mocka
        self.user_manager.db_manager.is_user_in_db.return_value = False
        self.user_manager.db_manager.add_user_into_db.return_value = True

        # Test poprawnego tworzenia użytkownika
        response = self.user_manager.handle_create_new_user("create", username="newuser", password="password123")
        self.assertEqual(response, "Użytkownik został dodany do bazy danych")

        # Test z istniejącym użytkownikiem
        self.user_manager.db_manager.is_user_in_db.return_value = True
        response = self.user_manager.handle_create_new_user("create", username="existinguser", password="password123")
        self.assertEqual(response, "Użytkownik już istnieje")

    def test_read_new_message(self):
        """Test odczytu nowych wiadomości"""
        # Przygotowanie mocka
        self.user_manager.current_user.is_logged = True
        self.user_manager.current_user.username = "testuser"
        test_messages = [
            ["Wiadomość 1", "sender1", "2024-03-20 10:00"],
            ["Wiadomość 2", "sender2", "2024-03-20 11:00"]
        ]
        self.user_manager.db_manager.get_all_new_messages_user.return_value = test_messages

        # Test odczytu nowych wiadomości
        response = self.user_manager.handle_read_new_message("read")
        self.assertIn("Wiadomość 1", response)
        self.assertIn("Wiadomość 2", response)

        # Test braku nowych wiadomości
        self.user_manager.db_manager.get_all_new_messages_user.return_value = []
        response = self.user_manager.handle_read_new_message("read")
        self.assertEqual(response, "Nie masz nowych wiadomości")

    def test_delete_user(self):
        """Test usuwania użytkownika"""
        # Przygotowanie mocka
        self.user_manager.current_user.is_logged = True
        self.user_manager.current_user.username = "admin"
        self.user_manager.current_user.role = "admin"
        self.user_manager.db_manager.delete_user_from_db.return_value = True

        # Test poprawnego usunięcia użytkownika
        response = self.user_manager.handle_delete_user("delete", username="usertodelete")
        self.assertEqual(response, "Użytkownik został usunięty")

        # Test usunięcia samego siebie
        response = self.user_manager.handle_delete_user("delete", username="admin")
        self.assertEqual(response, "Nie masz uprawnień do tej komendy")

    def test_edit_user_role(self):
        """Test edycji roli użytkownika"""
        # Przygotowanie mocka
        self.user_manager.current_user.is_logged = True
        self.user_manager.current_user.role = "admin"
        self.user_manager.db_manager.is_user_in_db.return_value = True
        self.user_manager.db_manager.edit_user_role_in_db.return_value = True

        # Test poprawnej zmiany roli
        response = self.user_manager.handle_edit_user_role("edit", username="user", new_role="admin")
        self.assertEqual(response, "Rola została zmieniona")

        # Test z nieistniejącym użytkownikiem
        self.user_manager.db_manager.is_user_in_db.return_value = False
        response = self.user_manager.handle_edit_user_role("edit", username="nonexistent", new_role="admin")
        self.assertEqual(response, "Nie masz uprawnień do tej komendy lub użytkownik nie istnieje")


if __name__ == '__main__':
    unittest.main()