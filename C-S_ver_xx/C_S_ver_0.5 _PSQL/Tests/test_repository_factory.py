import unittest
from unittest.mock import patch, Mock, MagicMock
import sys
from BLL.RepositoryFactory import RepositoryFactory
from DAL.json_repository import JsonRepository
from DAL.base_repository import BaseRepository

class TestRepositoryFactory(unittest.TestCase):
    
    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem"""
        self.factory = RepositoryFactory()
    
    # ============= TESTS FOR JSON DATABASE TYPE =============
    
    @patch('BLL.RepositoryFactory.DATABASE_TYPE', 'JSON')
    @patch('BLL.RepositoryFactory.PATH_USERS_DB', 'test_users.json')
    def test_create_users_repository_json_type(self):
        """Test tworzenia users repository dla typu JSON"""
        repository = RepositoryFactory.create_users_repository()
        
        # Sprawdzenie czy zwrócono JsonRepository
        self.assertIsInstance(repository, JsonRepository)
        self.assertIsInstance(repository, BaseRepository)
        
        # Sprawdzenie czy repository ma poprawne ustawienia
        self.assertEqual(repository.file_path, 'test_users.json')
        self.assertEqual(repository.collection_name, 'users')
    
    @patch('BLL.RepositoryFactory.DATABASE_TYPE', 'JSON')
    @patch('BLL.RepositoryFactory.PATH_MESSAGES_DB', 'test_messages.json')
    def test_create_messages_repository_json_type(self):
        """Test tworzenia messages repository dla typu JSON"""
        repository = RepositoryFactory.create_messages_repository()
        
        # Sprawdzenie czy zwrócono JsonRepository
        self.assertIsInstance(repository, JsonRepository)
        self.assertIsInstance(repository, BaseRepository)
        
        # Sprawdzenie czy repository ma poprawne ustawienia
        self.assertEqual(repository.file_path, 'test_messages.json')
        self.assertEqual(repository.collection_name, 'messages')
    
    # ============= TESTS FOR SQL DATABASE TYPE =============
    
    @patch('BLL.RepositoryFactory.DATABASE_TYPE', 'SQL')
    def test_create_users_repository_sql_type_import_error(self):
        """Test błędu importu SqlRepository dla users repository"""
        with self.assertRaises(ImportError):
            RepositoryFactory.create_users_repository()
    
    @patch('BLL.RepositoryFactory.DATABASE_TYPE', 'SQL')
    def test_create_messages_repository_sql_type_import_error(self):
        """Test błędu importu SqlRepository dla messages repository"""
        with self.assertRaises(ImportError):
            RepositoryFactory.create_messages_repository()
    
    # ============= TESTS FOR INVALID DATABASE TYPE =============
    
    @patch('BLL.RepositoryFactory.DATABASE_TYPE', 'INVALID_TYPE')
    def test_create_users_repository_invalid_type(self):
        """Test błędu dla nieprawidłowego typu bazy danych - users repository"""
        with self.assertRaises(ValueError) as context:
            RepositoryFactory.create_users_repository()
        
        self.assertEqual(str(context.exception), "Unsupported database type: INVALID_TYPE")
    
    @patch('BLL.RepositoryFactory.DATABASE_TYPE', 'INVALID_TYPE')
    def test_create_messages_repository_invalid_type(self):
        """Test błędu dla nieprawidłowego typu bazy danych - messages repository"""
        with self.assertRaises(ValueError) as context:
            RepositoryFactory.create_messages_repository()
        
        self.assertEqual(str(context.exception), "Unsupported database type: INVALID_TYPE")
    
    # ============= TESTS FOR EDGE CASES =============
    
    @patch('BLL.RepositoryFactory.DATABASE_TYPE', '')
    def test_create_users_repository_empty_database_type(self):
        """Test obsługi pustego DATABASE_TYPE"""
        with self.assertRaises(ValueError) as context:
            RepositoryFactory.create_users_repository()
        
        self.assertEqual(str(context.exception), "Unsupported database type: ")
    
    @patch('BLL.RepositoryFactory.DATABASE_TYPE', None)
    def test_create_users_repository_none_database_type(self):
        """Test obsługi None jako DATABASE_TYPE"""
        with self.assertRaises(ValueError) as context:
            RepositoryFactory.create_users_repository()
        
        self.assertEqual(str(context.exception), "Unsupported database type: None")
    
    @patch('BLL.RepositoryFactory.DATABASE_TYPE', 'json')  # lowercase
    def test_create_users_repository_case_sensitive(self):
        """Test czy DATABASE_TYPE jest case-sensitive"""
        with self.assertRaises(ValueError) as context:
            RepositoryFactory.create_users_repository()
        
        self.assertEqual(str(context.exception), "Unsupported database type: json")
    
    # ============= TESTS FOR METHOD CONSISTENCY =============
    
    @patch('BLL.RepositoryFactory.DATABASE_TYPE', 'JSON')
    @patch('BLL.RepositoryFactory.PATH_USERS_DB', 'users.json')
    @patch('BLL.RepositoryFactory.PATH_MESSAGES_DB', 'messages.json')
    def test_both_methods_return_same_type_json(self):
        """Test czy obie metody zwracają ten sam typ dla JSON"""
        users_repo = RepositoryFactory.create_users_repository()
        messages_repo = RepositoryFactory.create_messages_repository()
        
        # Sprawdzenie czy oba są JsonRepository
        self.assertIsInstance(users_repo, JsonRepository)
        self.assertIsInstance(messages_repo, JsonRepository)
        self.assertEqual(type(users_repo), type(messages_repo))
    
    @patch('BLL.RepositoryFactory.DATABASE_TYPE', 'SQL')
    def test_both_methods_return_same_error_sql(self):
        """Test czy obie metody zwracają ten sam błąd dla SQL"""
        with self.assertRaises(ImportError):
            RepositoryFactory.create_users_repository()
        
        with self.assertRaises(ImportError):
            RepositoryFactory.create_messages_repository()
    
    # ============= TESTS FOR RETURN TYPE VALIDATION =============
    
    @patch('BLL.RepositoryFactory.DATABASE_TYPE', 'JSON')
    @patch('config.PATH_USERS_DB', 'users.json')
    def test_users_repository_implements_base_repository(self):
        """Test czy users repository implementuje BaseRepository interface"""
        repository = RepositoryFactory.create_users_repository()
        
        # Sprawdzenie czy ma wszystkie wymagane metody BaseRepository
        required_methods = ['find_by_id', 'find_all', 'find_by_field', 'save', 'update', 'delete']
        for method in required_methods:
            self.assertTrue(hasattr(repository, method), 
                          f"Repository nie ma metody {method}")
            self.assertTrue(callable(getattr(repository, method)), 
                          f"Metoda {method} nie jest callable")
    
    @patch('BLL.RepositoryFactory.DATABASE_TYPE', 'JSON')
    @patch('config.PATH_MESSAGES_DB', 'messages.json')
    def test_messages_repository_implements_base_repository(self):
        """Test czy messages repository implementuje BaseRepository interface"""
        repository = RepositoryFactory.create_messages_repository()
        
        # Sprawdzenie czy ma wszystkie wymagane metody BaseRepository
        required_methods = ['find_by_id', 'find_all', 'find_by_field', 'save', 'update', 'delete']
        for method in required_methods:
            self.assertTrue(hasattr(repository, method), 
                          f"Repository nie ma metody {method}")
            self.assertTrue(callable(getattr(repository, method)), 
                          f"Metoda {method} nie jest callable")
    
    # ============= TESTS FOR STATIC METHODS =============
    
    def test_factory_methods_are_static(self):
        """Test czy metody factory są statyczne"""
        # Sprawdzenie czy można wywołać metody bez tworzenia instancji
        self.assertTrue(callable(RepositoryFactory.create_users_repository))
        self.assertTrue(callable(RepositoryFactory.create_messages_repository))
        
        # Sprawdzenie czy metody są oznaczone jako staticmethod
        self.assertIsInstance(RepositoryFactory.__dict__['create_users_repository'], staticmethod)
        self.assertIsInstance(RepositoryFactory.__dict__['create_messages_repository'], staticmethod)
    
    # ============= TESTS FOR CONFIGURATION DEPENDENCIES =============
    
    @patch('BLL.RepositoryFactory.DATABASE_TYPE', 'JSON')
    @patch('config.PATH_USERS_DB')
    def test_users_repository_uses_config_path(self, mock_path):
        """Test czy users repository używa ścieżki z konfiguracji"""
        mock_path = '/custom/path/users.json'
        
        with patch('BLL.RepositoryFactory.PATH_USERS_DB', mock_path):
            repository = RepositoryFactory.create_users_repository()
            self.assertEqual(repository.file_path, mock_path)
    
    @patch('BLL.RepositoryFactory.DATABASE_TYPE', 'JSON')
    @patch('config.PATH_MESSAGES_DB')
    def test_messages_repository_uses_config_path(self, mock_path):
        """Test czy messages repository używa ścieżki z konfiguracji"""
        mock_path = '/custom/path/messages.json'
        
        with patch('BLL.RepositoryFactory.PATH_MESSAGES_DB', mock_path):
            repository = RepositoryFactory.create_messages_repository()
            self.assertEqual(repository.file_path, mock_path)
    
    # ============= TESTS FOR IMPORT ERRORS =============
    # (SQL import errors are covered in SQL type tests above)
    
    # ============= INTEGRATION TESTS =============
    
    @patch('BLL.RepositoryFactory.DATABASE_TYPE', 'JSON')
    @patch('BLL.RepositoryFactory.PATH_USERS_DB', 'test_users.json')
    @patch('BLL.RepositoryFactory.PATH_MESSAGES_DB', 'test_messages.json')
    def test_factory_creates_different_instances(self):
        """Test czy factory tworzy różne instancje dla każdego wywołania"""
        users_repo1 = RepositoryFactory.create_users_repository()
        users_repo2 = RepositoryFactory.create_users_repository()
        messages_repo1 = RepositoryFactory.create_messages_repository()
        
        # Sprawdzenie czy to są różne obiekty
        self.assertNotEqual(id(users_repo1), id(users_repo2))
        self.assertNotEqual(id(users_repo1), id(messages_repo1))
        
        # Ale tego samego typu
        self.assertEqual(type(users_repo1), type(users_repo2))
        self.assertEqual(type(users_repo1), type(messages_repo1))
    
    @patch('BLL.RepositoryFactory.DATABASE_TYPE', 'JSON')
    def test_factory_preserves_collection_names(self):
        """Test czy factory zachowuje poprawne nazwy kolekcji"""
        with patch('BLL.RepositoryFactory.PATH_USERS_DB', 'test.json'), \
             patch('BLL.RepositoryFactory.PATH_MESSAGES_DB', 'test.json'):
            
            users_repo = RepositoryFactory.create_users_repository()
            messages_repo = RepositoryFactory.create_messages_repository()
            
            # Mimo tej samej ścieżki pliku, nazwy kolekcji powinny być różne
            self.assertEqual(users_repo.collection_name, 'users')
            self.assertEqual(messages_repo.collection_name, 'messages')
            self.assertNotEqual(users_repo.collection_name, messages_repo.collection_name)

if __name__ == '__main__':
    unittest.main()