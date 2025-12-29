import unittest
from unittest.mock import patch
from Models.user import User

class TestUser(unittest.TestCase):
    
    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem"""
        self.user = User()

    def test_user_constructor_default_values(self):
        """Test domyślnych wartości konstruktora User"""
        user = User()
        
        self.assertIsNone(user.id)
        self.assertIsNone(user.username)
        self.assertIsNone(user.password)
        self.assertEqual(user.role, 'user')
        self.assertFalse(user.is_logged)
        self.assertIsNone(user.login_time)
        self.assertIsNone(user.create_time)

    def test_user_attributes_assignment(self):
        """Test przypisywania wartości do atrybutów User"""
        user = User()
        
        user.id = "user_123"
        user.username = "testuser"
        user.password = "hashedpassword123"
        user.role = "admin"
        user.is_logged = True
        user.login_time = "2024-01-01T12:00:00"
        user.create_time = "2024-01-01T10:00:00"
        
        self.assertEqual(user.id, "user_123")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.password, "hashedpassword123")
        self.assertEqual(user.role, "admin")
        self.assertTrue(user.is_logged)
        self.assertEqual(user.login_time, "2024-01-01T12:00:00")
        self.assertEqual(user.create_time, "2024-01-01T10:00:00")

    def test_user_role_user_permissions(self):
        """Test uprawnień dla roli 'user'"""
        user = User()
        user.role = 'user'
        
        # Komendy dozwolone dla użytkownika
        self.assertTrue(user.is_user_allowed_to_command("send"))
        self.assertTrue(user.is_user_allowed_to_command("read"))
        self.assertTrue(user.is_user_allowed_to_command("read-u"))
        self.assertTrue(user.is_user_allowed_to_command("read-a"))
        self.assertTrue(user.is_user_allowed_to_command("login"))
        self.assertTrue(user.is_user_allowed_to_command("logout"))
        self.assertTrue(user.is_user_allowed_to_command("help"))
        self.assertTrue(user.is_user_allowed_to_command("create"))
        
        # Komendy niedozwolone dla użytkownika
        self.assertFalse(user.is_user_allowed_to_command("read-o"))
        self.assertFalse(user.is_user_allowed_to_command("info"))
        self.assertFalse(user.is_user_allowed_to_command("delete"))
        self.assertFalse(user.is_user_allowed_to_command("edit"))

    def test_admin_role_permissions(self):
        """Test uprawnień dla roli 'admin'"""
        user = User()
        user.role = 'admin'
        
        # Wszystkie komendy powinny być dozwolone dla administratora
        admin_commands = [
            "send", "read", "read-u", "read-a", "read-o",
            "login", "logout", "help", "info", "create", "delete", "edit"
        ]
        
        for command in admin_commands:
            with self.subTest(command=command):
                self.assertTrue(user.is_user_allowed_to_command(command))

    def test_is_user_allowed_to_command_with_different_roles(self):
        """Test metody is_user_allowed_to_command dla różnych ról"""
        # Test dla roli user
        user_role = User()
        user_role.role = 'user'
        
        # Test dla roli admin
        admin_role = User()
        admin_role.role = 'admin'
        
        # Porównanie uprawnień między rolami
        test_cases = [
            ("send", True, True),
            ("read", True, True),
            ("read-o", False, True),  # tylko admin
            ("info", False, True),    # tylko admin
            ("delete", False, True),  # tylko admin
            ("edit", False, True),    # tylko admin
        ]
        
        for command, user_expected, admin_expected in test_cases:
            with self.subTest(command=command):
                self.assertEqual(user_role.is_user_allowed_to_command(command), user_expected)
                self.assertEqual(admin_role.is_user_allowed_to_command(command), admin_expected)

    def test_user_login_workflow(self):
        """Test workflow logowania użytkownika"""
        user = User()
        
        # Początkowy stan - niezalogowany
        self.assertFalse(user.is_logged)
        self.assertIsNone(user.login_time)
        
        # Symulacja logowania
        user.username = "testuser"
        user.password = "hashed_password"
        user.is_logged = True
        user.login_time = "2024-01-01T12:00:00"
        
        # Sprawdzenie stanu po zalogowaniu
        self.assertTrue(user.is_logged)
        self.assertIsNotNone(user.login_time)
        self.assertEqual(user.username, "testuser")

    def test_user_role_change(self):
        """Test zmiany roli użytkownika"""
        user = User()
        
        # Domyślna rola
        self.assertEqual(user.role, 'user')
        self.assertFalse(user.is_user_allowed_to_command("delete"))
        
        # Zmiana na administratora
        user.role = 'admin'
        self.assertEqual(user.role, 'admin')
        self.assertTrue(user.is_user_allowed_to_command("delete"))

    def test_user_data_types(self):
        """Test typów danych atrybutów User"""
        user = User()
        
        user.id = "123"
        user.username = "testuser"
        user.password = "password"
        user.role = "admin"
        user.is_logged = True
        user.login_time = "2024-01-01T12:00:00"
        user.create_time = "2024-01-01T10:00:00"
        
        self.assertIsInstance(user.id, str)
        self.assertIsInstance(user.username, str)
        self.assertIsInstance(user.password, str)
        self.assertIsInstance(user.role, str)
        self.assertIsInstance(user.is_logged, bool)
        self.assertIsInstance(user.login_time, str)
        self.assertIsInstance(user.create_time, str)

    def test_user_empty_values(self):
        """Test obsługi pustych wartości"""
        user = User()
        
        user.id = ""
        user.username = ""
        user.password = ""
        user.login_time = ""
        user.create_time = ""
        
        self.assertEqual(user.id, "")
        self.assertEqual(user.username, "")
        self.assertEqual(user.password, "")
        self.assertEqual(user.login_time, "")
        self.assertEqual(user.create_time, "")

    def test_user_permission_edge_cases(self):
        """Test przypadków brzegowych dla uprawnień"""
        user = User()
        
        # Test z pustą rolą (może powodować KeyError)
        user.role = ""
        with self.assertRaises(KeyError):
            user.is_user_allowed_to_command("send")
        
        # Test z nieistniejącą rolą
        user.role = "nonexistent_role"
        with self.assertRaises(KeyError):
            user.is_user_allowed_to_command("send")

    def test_user_command_edge_cases(self):
        """Test przypadków brzegowych dla komend"""
        user = User()
        user.role = 'user'
        
        # Test z nieistniejącą komendą
        with self.assertRaises(KeyError):
            user.is_user_allowed_to_command("nonexistent_command")
        
        # Test z pustą komendą
        with self.assertRaises(KeyError):
            user.is_user_allowed_to_command("")

    def test_user_boolean_operations(self):
        """Test operacji boolean na użytkowniku"""
        user = User()
        
        # Test is_logged jako boolean
        self.assertFalse(user.is_logged)
        user.is_logged = True
        self.assertTrue(user.is_logged)
        user.is_logged = False
        self.assertFalse(user.is_logged)

    def test_user_permission_consistency(self):
        """Test spójności uprawnień między różnymi komendami"""
        user = User()
        admin = User()
        
        user.role = 'user'
        admin.role = 'admin'
        
        # Admin powinien mieć wszystkie uprawnienia użytkownika plus dodatkowe
        user_allowed_commands = []
        admin_allowed_commands = []
        
        all_commands = [
            "send", "read", "read-u", "read-a", "read-o",
            "login", "logout", "help", "info", "create", "delete", "edit"
        ]
        
        for command in all_commands:
            if user.is_user_allowed_to_command(command):
                user_allowed_commands.append(command)
            if admin.is_user_allowed_to_command(command):
                admin_allowed_commands.append(command)
        
        # Admin powinien mieć co najmniej tyle uprawnień co user
        for command in user_allowed_commands:
            self.assertIn(command, admin_allowed_commands, 
                         f"Admin should have at least all user permissions, missing: {command}")

    def test_user_state_transitions(self):
        """Test przejść stanów użytkownika"""
        user = User()
        
        # Stan początkowy
        self.assertIsNone(user.username)
        self.assertFalse(user.is_logged)
        
        # Rejestracja
        user.username = "newuser"
        user.password = "hashed_password"
        user.create_time = "2024-01-01T10:00:00"
        
        self.assertIsNotNone(user.username)
        self.assertFalse(user.is_logged)  # nadal niezalogowany
        
        # Logowanie
        user.is_logged = True
        user.login_time = "2024-01-01T12:00:00"
        
        self.assertTrue(user.is_logged)
        
        # Wylogowanie
        user.is_logged = False
        
        self.assertFalse(user.is_logged)
        # login_time może pozostać jako historia ostatniego logowania

if __name__ == '__main__':
    unittest.main()