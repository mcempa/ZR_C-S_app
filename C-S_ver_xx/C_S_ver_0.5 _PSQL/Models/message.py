import time
import uuid
import secrets
from datetime import datetime
from config import ID_RANDOM_BITS, ID_HEX_BYTES


class Message():
    def __init__(self):
        self.id = None  # ID będzie przypisane przez serwis
        self.username = None
        self.sender = None
        self.text = None
        self.send_time = datetime.now().strftime('%Y-%m-%d godz. %H:%M')
        self.read_time = None
        self.is_read = 0

    def _generate_id(self):
        """Generuje unikalny ID używając UUID4 (bezpieczny i unikalny)"""
        return str(uuid.uuid4())
    
    def _generate_numeric_id(self):
        """Generuje unikalny numeryczny ID (timestamp + losowe bity)"""
        timestamp_ms = int(time.time() * 1000)
        random_bits = secrets.randbits(ID_RANDOM_BITS)  # Configurable bits of randomness
        return (timestamp_ms << ID_RANDOM_BITS) | random_bits
    
    def _generate_short_id(self):
        """Generuje krótki losowy ID (8 znaków hex)"""
        return secrets.token_hex(ID_HEX_BYTES)  # Configurable hex bytes
    
    def _generate_send_time(self):
        return datetime.now().strftime('%Y-%m-%d godz. %H:%M')
    
    def _generate_read_time(self):
        return datetime.now().strftime('%Y-%m-%d godz. %H:%M')
    
    def to_dict(self):
        """Konwertuje obiekt Message do słownika dla JSON"""
        return {
            'id': self.id,
            'username': self.username,
            'sender': self.sender,
            'text': self.text,
            'send_time': self.send_time,
            'read_time': self.read_time,
            'is_read': self.is_read
        }
   