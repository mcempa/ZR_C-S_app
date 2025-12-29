"""
Data Transfer Objects (DTO) dla komunikacji klient-serwer
Uproszczony protokół komunikacyjny zachowujący wzorce Factory i Repository
"""
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import json

@dataclass
class RequestDTO:
    """Data Transfer Object dla żądań klienta"""
    command: str
    data: Dict[str, Any]
    
    def to_json(self) -> str:
        """Konwertuje DTO do JSON string"""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, json_str: str) -> 'RequestDTO':
        """Tworzy DTO z JSON string"""
        data_dict = json.loads(json_str)
        return cls(
            command=data_dict['command'],
            data=data_dict.get('data', {})
        )
    
    @classmethod
    def from_dict(cls, data_dict: Dict) -> 'RequestDTO':
        """Tworzy DTO ze słownika"""
        return cls(
            command=data_dict['command'],
            data=data_dict.get('data', {})
        )

@dataclass
class ResponseDTO:
    """Data Transfer Object dla odpowiedzi serwera"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    
    def to_json(self) -> str:
        """Konwertuje DTO do JSON string"""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ResponseDTO':
        """Tworzy DTO z JSON string"""
        data_dict = json.loads(json_str)
        return cls(
            success=data_dict['success'],
            message=data_dict['message'],
            data=data_dict.get('data'),
            error_code=data_dict.get('error_code')
        )
    
    @classmethod
    def success_response(cls, message: str, data: Optional[Dict] = None) -> 'ResponseDTO':
        """Tworzy pozytywną odpowiedź"""
        return cls(success=True, message=message, data=data)
    
    @classmethod
    def error_response(cls, message: str, error_code: Optional[str] = None) -> 'ResponseDTO':
        """Tworzy odpowiedź z błędem"""
        return cls(success=False, message=message, error_code=error_code)

class MessageProtocol:
    """
    Klasa pomocnicza do zarządzania protokołem komunikacyjnym
    
    Nowy format:
    REQUEST:  {"command": "login", "data": {"username": "test", "password": "123"}}
    RESPONSE: {"success": true, "message": "Zalogowano", "data": {...}}
    
    Zamiast starego formatu:
    REQUEST:  ["login", {"username": "test", "password": "123"}]
    RESPONSE: "Zalogowano" (zwykły string)
    """
    
    @staticmethod
    def create_request(command: str, data: Dict[str, Any] = None) -> RequestDTO:
        """Tworzy uproszczone żądanie"""
        return RequestDTO(command=command, data=data or {})
    
    @staticmethod
    def create_success_response(message: str, data: Dict = None) -> ResponseDTO:
        """Tworzy pozytywną odpowiedź"""
        return ResponseDTO.success_response(message, data)
    
    @staticmethod
    def create_error_response(message: str, error_code: str = None) -> ResponseDTO:
        """Tworzy odpowiedź z błędem"""
        return ResponseDTO.error_response(message, error_code)
