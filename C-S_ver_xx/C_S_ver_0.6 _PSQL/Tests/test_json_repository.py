import unittest
import json
import os
import tempfile
from DAL.json_repository import JsonRepository

class TestJsonRepository(unittest.TestCase):
    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.json')
        self.collection_name = "test_items"
        
        # Inicjalizacja przykładowych danych
        self.initial_data = {
            self.collection_name: [
                {"id": "1", "name": "Item 1", "value": 100},
                {"id": "2", "name": "Item 2", "value": 200},
                {"id": "3", "name": "Item 3", "value": 300}
            ]
        }
        
        # Zapisanie danych do tymczasowego pliku
        json.dump(self.initial_data, self.temp_file)
        self.temp_file.close()
        
        # Inicjalizacja JsonRepository
        self.repository = JsonRepository(self.temp_file.name, self.collection_name)

    def tearDown(self):
        """Czyszczenie po testach"""
        os.unlink(self.temp_file.name)

    def test_find_by_id_existing(self):
        """Test znajdowania istniejącego elementu po ID"""
        item = self.repository.find_by_id("1")
        self.assertIsNotNone(item)
        self.assertEqual(item["id"], "1")
        self.assertEqual(item["name"], "Item 1")
        self.assertEqual(item["value"], 100)

    def test_find_by_id_non_existing(self):
        """Test znajdowania nieistniejącego elementu po ID"""
        item = self.repository.find_by_id("999")
        self.assertIsNone(item)

    def test_find_all(self):
        """Test pobierania wszystkich elementów"""
        items = self.repository.find_all()
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["id"], "1")
        self.assertEqual(items[1]["id"], "2")
        self.assertEqual(items[2]["id"], "3")

    def test_find_by_field_existing(self):
        """Test znajdowania elementów po wartości pola"""
        items = self.repository.find_by_field("name", "Item 1")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], "1")

    def test_find_by_field_non_existing(self):
        """Test znajdowania elementów po nieistniejącej wartości pola"""
        items = self.repository.find_by_field("name", "Non-existent Item")
        self.assertEqual(len(items), 0)

    def test_find_by_field_multiple_results(self):
        """Test znajdowania wielu elementów po wartości pola"""
        # Dodajemy element z taką samą wartością
        new_item = {"id": "4", "name": "Item 1", "value": 400}
        self.repository.save(new_item)
        
        items = self.repository.find_by_field("name", "Item 1")
        self.assertEqual(len(items), 2)

    def test_save_new_item(self):
        """Test zapisywania nowego elementu"""
        new_item = {"id": "4", "name": "Item 4", "value": 400}
        result = self.repository.save(new_item)
        
        self.assertTrue(result)
        
        # Sprawdzenie czy element został dodany
        items = self.repository.find_all()
        self.assertEqual(len(items), 4)
        
        saved_item = self.repository.find_by_id("4")
        self.assertIsNotNone(saved_item)
        self.assertEqual(saved_item["name"], "Item 4")

    def test_update_existing_item(self):
        """Test aktualizacji istniejącego elementu"""
        update_data = {"name": "Updated Item 1", "value": 150}
        result = self.repository.update("1", update_data)
        
        self.assertTrue(result)
        
        # Sprawdzenie czy element został zaktualizowany
        updated_item = self.repository.find_by_id("1")
        self.assertIsNotNone(updated_item)
        self.assertEqual(updated_item["name"], "Updated Item 1")
        self.assertEqual(updated_item["value"], 150)
        self.assertEqual(updated_item["id"], "1")  # ID nie powinno się zmienić

    def test_update_non_existing_item(self):
        """Test aktualizacji nieistniejącego elementu"""
        update_data = {"name": "Non-existent Item", "value": 999}
        result = self.repository.update("999", update_data)
        
        self.assertFalse(result)

    def test_delete_existing_item(self):
        """Test usuwania istniejącego elementu"""
        result = self.repository.delete("1")
        
        self.assertTrue(result)
        
        # Sprawdzenie czy element został usunięty
        items = self.repository.find_all()
        self.assertEqual(len(items), 2)
        
        deleted_item = self.repository.find_by_id("1")
        self.assertIsNone(deleted_item)

    def test_delete_non_existing_item(self):
        """Test usuwania nieistniejącego elementu"""
        result = self.repository.delete("999")
        
        self.assertTrue(result)  # Metoda zwraca True nawet jeśli element nie istniał
        
        # Sprawdzenie że liczba elementów się nie zmieniła
        items = self.repository.find_all()
        self.assertEqual(len(items), 3)

    def test_load_data_from_non_existing_file(self):
        """Test wczytywania danych z nieistniejącego pliku"""
        non_existing_repo = JsonRepository("non_existing_file.json", "test")
        data = non_existing_repo._load_data()
        
        self.assertIsInstance(data, dict)
        self.assertIn("test", data)
        self.assertEqual(data["test"], [])

    def test_save_data_creates_valid_json(self):
        """Test czy _save_data tworzy prawidłowy plik JSON"""
        test_data = {
            self.collection_name: [
                {"id": "test", "name": "Test Item"}
            ]
        }
        
        result = self.repository._save_data(test_data)
        self.assertTrue(result)
        
        # Sprawdzenie czy plik został poprawnie zapisany
        with open(self.temp_file.name, 'r', encoding='utf-8') as file:
            loaded_data = json.load(file)
        
        self.assertEqual(loaded_data, test_data)

    def test_save_and_load_data_consistency(self):
        """Test spójności danych po zapisie i odczycie"""
        original_items = self.repository.find_all()
        
        # Dodajemy nowy element
        new_item = {"id": "5", "name": "Item 5", "value": 500}
        self.repository.save(new_item)
        
        # Tworzymy nowe repozytorium dla tego samego pliku
        new_repo = JsonRepository(self.temp_file.name, self.collection_name)
        loaded_items = new_repo.find_all()
        
        self.assertEqual(len(loaded_items), len(original_items) + 1)
        self.assertIsNotNone(new_repo.find_by_id("5"))

    def test_empty_collection_operations(self):
        """Test operacji na pustej kolekcji"""
        empty_repo = JsonRepository("empty_test.json", "empty_collection")
        
        # Test find_all na pustej kolekcji
        items = empty_repo.find_all()
        self.assertEqual(len(items), 0)
        
        # Test find_by_id na pustej kolekcji
        item = empty_repo.find_by_id("1")
        self.assertIsNone(item)
        
        # Test find_by_field na pustej kolekcji
        items = empty_repo.find_by_field("name", "test")
        self.assertEqual(len(items), 0)
        
        # Czyszczenie
        if os.path.exists("empty_test.json"):
            os.unlink("empty_test.json")

if __name__ == '__main__':
    unittest.main()