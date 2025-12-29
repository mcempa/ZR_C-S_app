import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from DAL.base_repository import BaseRepository

class JsonRepository(BaseRepository):
    def __init__(self, file_path: str, collection_name: str):
        self.file_path = file_path
        self.collection_name = collection_name

    def _load_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Wczytuje wszystkie dane z pliku JSON"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {self.collection_name: []}

    def _save_data(self, data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Zapisuje wszystkie dane do pliku JSON"""
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return True

    def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        data = self._load_data()
        for item in data[self.collection_name]:
            if item.get("id") == id:
                return item
        return None

    def find_all(self) -> List[Dict[str, Any]]:
        data = self._load_data()
        return data[self.collection_name]

    def find_by_field(self, field: str, value: Any) -> List[Dict[str, Any]]:
        data = self._load_data()
        return [item for item in data[self.collection_name] if item.get(field) == value]

    def save(self, data: Dict[str, Any]) -> bool:
        all_data = self._load_data()
        all_data[self.collection_name].append(data)
        return self._save_data(all_data)

    def update(self, id: str, data: Dict[str, Any]) -> bool:
        all_data = self._load_data()
        for i, item in enumerate(all_data[self.collection_name]):
            if item.get("id") == id:
                all_data[self.collection_name][i] = {**item, **data}
                return self._save_data(all_data)
        return False

    def delete(self, id: str) -> bool:
        all_data = self._load_data()
        all_data[self.collection_name] = [
            item for item in all_data[self.collection_name] 
            if item.get("id") != id
        ]
        return self._save_data(all_data) 
    
    
   