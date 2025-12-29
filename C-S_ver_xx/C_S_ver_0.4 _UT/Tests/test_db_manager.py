import unittest
import json
import os
import tempfile
import bcrypt
from datetime import datetime
from BLL.DbManager import DbManager
from DAL.json_repository import JsonRepository
from Models.message import Message

class TestDbManager(unittest.TestCase):
    def setUp(self):
        # Tworzenie tymczasowych plików dla testów
        self.temp_users_db = tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.json')
        self.temp_messages_db = tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.json')
        
        # Hashowanie hasła testowego
        test_password = "test_pass"
        hashed_password = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
        
        # Inicjalizacja przykładowych danych
        self.users_data = {
            "users": [
                {   "id": "1",
                    "username": "test_user",
                    "password": hashed_password.decode('utf-8'),  # Konwersja na string do zapisu w JSON
                    "role": "user",
                    "login_time": datetime.now().isoformat()
                }
            ]
        }
        
        self.messages_data = {
            "messages": [
                {
                    "id": "1",
                    "text": "Test message",
                    "username": "test_user",
                    "sender": "sender_user",
                    "send_time": datetime.now().strftime("%Y-%m-%d godz. %H:%M"),
                    "is_read": 0,
                    "read_time": None
                }
            ]
        }
        
        # Zapisanie danych do tymczasowych plików
        json.dump(self.users_data, self.temp_users_db)
        json.dump(self.messages_data, self.temp_messages_db)
        
        self.temp_users_db.close()
        self.temp_messages_db.close()
        
        # Inicjalizacja DbManager z tymczasowymi plikami
        self.db_manager = DbManager()
        self.db_manager.users_repository = JsonRepository(self.temp_users_db.name, "users")
        self.db_manager.messages_repository = JsonRepository(self.temp_messages_db.name, "messages")

    def tearDown(self):
        # Usuwanie tymczasowych plików
        os.unlink(self.temp_users_db.name)
        os.unlink(self.temp_messages_db.name)

    
    def test_add_message_into_db(self):
        message = Message()
        message.id = "2"
        message.text = "New test message"
        message.username = "test_user"
        message.sender = "new_sender"
        message.send_time = datetime.now().strftime('%Y-%m-%d godz. %H:%M')
        message.read_time = None
        message.is_read = 0
        
        result = self.db_manager.add_message_into_db(message)
        self.assertTrue(result)
        
        # Sprawdzenie czy wiadomość została dodana
        messages = self.db_manager.messages_repository.find_all()
        self.assertEqual(len(messages), 2)

    def test_delete_message_from_db(self):
        result = self.db_manager.delete_message_from_db("1", "test_user")
        self.assertTrue(result)
        
        # Sprawdzenie czy wiadomość została usunięta
        messages = self.db_manager.messages_repository.find_all()
        self.assertEqual(len(messages), 0)

    def test_get_all_messages_user(self):
        messages = self.db_manager.get_all_messages_user("test_user")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], "Test message")

    def test_get_all_messages_user_from_sender(self):
        messages = self.db_manager.get_all_messages_user_from_sender("test_user", "sender_user")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], "Test message")

    def test_get_all_new_messages_user(self):
        messages = self.db_manager.get_all_new_messages_user("test_user")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0][0], "Test message")

    def test_change_message_status_into_read(self):
        result = self.db_manager.change_message_status_into_read("test_user")
        self.assertTrue(result)
        
        # Sprawdzenie czy status został zmieniony
        message = self.db_manager.messages_repository.find_by_id("1")
        self.assertEqual(message["is_read"], 1)

    def test_add_user_into_db(self):
        new_password = "new_pass"
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        new_user = {
            "id": "2",
            "username": "new_user",
            "password": hashed_password.decode('utf-8'),
            "role": "user",
            "login_time": datetime.now().isoformat()
        }
        
        result = self.db_manager.add_user_into_db(new_user)
        self.assertTrue(result)
        
        # Sprawdzenie czy użytkownik został dodany
        users = self.db_manager.users_repository.find_all()
        self.assertEqual(len(users), 2)

    def test_delete_user_from_db(self):
        # Sprawdzenie czy użytkownik istnieje przed usunięciem
        self.assertTrue(self.db_manager.is_user_in_db("test_user"))
        
        # Usunięcie użytkownika
        result = self.db_manager.delete_user_from_db("test_user")
        self.assertTrue(result)
        
        # Sprawdzenie czy użytkownik został usunięty
        self.assertFalse(self.db_manager.is_user_in_db("test_user"))

    def test_edit_user_role_in_db(self):
        result = self.db_manager.edit_user_role_in_db("test_user", "admin")
        self.assertTrue(result)
        
        # Sprawdzenie czy rola została zmieniona
        user = self.db_manager.users_repository.find_by_id("1")
        self.assertEqual(user["role"], "admin")

    def test_is_user_in_db(self):
        # Test dla istniejącego użytkownika
        result = self.db_manager.is_user_in_db("test_user")
        self.assertTrue(result)
        
        # Test dla nieistniejącego użytkownika
        result = self.db_manager.is_user_in_db("non_existent_user")
        self.assertFalse(result)

    def test_is_message_in_db(self):
        # Test dla istniejącej wiadomości
        result = self.db_manager.is_message_in_db("1")
        self.assertTrue(result)
        
        # Test dla nieistniejącej wiadomości
        result = self.db_manager.is_message_in_db("999")
        self.assertFalse(result)

    def test_is_user_password_in_db(self):
        # Test dla poprawnego hasła
        result = self.db_manager.is_user_password_in_db("test_user", self.users_data["users"][0]["password"])
        self.assertTrue(result)
        
        # Test dla niepoprawnego hasła
        result = self.db_manager.is_user_password_in_db("test_user", "wrong_pass")
        self.assertFalse(result)

    def test_get_user_info(self):
        # Test dla istniejącego użytkownika
        user_info = self.db_manager.get_user_info("test_user")
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info["username"], "test_user")
        self.assertEqual(user_info["role"], "user")
        self.assertIn("login_time", user_info)
        self.assertNotIn("password", user_info)  # Sprawdzenie czy hasło nie jest zwracane
        
        # Test dla nieistniejącego użytkownika
        non_existent_user = self.db_manager.get_user_info("non_existent_user")
        self.assertIsNone(non_existent_user)

    def test_get_user_password(self):
        password = self.db_manager.get_user_password("test_user")
        self.assertEqual(password, self.users_data["users"][0]["password"])

    def test_get_user_role(self):
        # Test dla istniejącego użytkownika
        role = self.db_manager.get_user_role("test_user")
        self.assertEqual(role, "user")
        
        # Test dla nieistniejącego użytkownika
        role = self.db_manager.get_user_role("non_existent_user")
        self.assertIsNone(role)
        
        # Test dla użytkownika z inną rolą
        self.db_manager.edit_user_role_in_db("test_user", "admin")
        role = self.db_manager.get_user_role("test_user")
        self.assertEqual(role, "admin")
        
        # Sprawdzenie czy hasło nie jest zwracane
        user_info = self.db_manager.get_user_info("test_user")
        self.assertNotIn("password", user_info)

if __name__ == '__main__':
    unittest.main() 