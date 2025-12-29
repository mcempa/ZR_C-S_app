from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Znajduje rekord po ID i zwraca je"""
        pass

    @abstractmethod
    def find_all(self) -> List[Dict[str, Any]]:
        """Zwraca wszystkie rekordy z bazy danych"""
        pass

    @abstractmethod
    def find_by_field(self, field: str, value: Any) -> List[Dict[str, Any]]:
        """Znajduje rekordy po wartości danego pola"""
        pass

    @abstractmethod
    def save(self, data: Dict[str, Any]) -> bool:
        """Zapisuje nowy rekord"""
        pass

    @abstractmethod
    def update(self, id: str, data: Dict[str, Any]) -> bool:
        """Aktualizuje istniejący rekord"""
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        """Usuwa rekord"""
        pass 