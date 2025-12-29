from typing import List, Dict, Any, Optional
from DAL.base_repository import BaseRepository
from Database.conection import get_db_connection

from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PostgreSQLRepository(BaseRepository):
    """PostgreSQL implementation of BaseRepository"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.db = get_db_connection()
        
    def find_all(self) -> List[Dict[str, Any]]:
        """Retrieve all records from the table"""
        query = f"SELECT * FROM {self.table_name}"
        
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                results = cursor.fetchall()
                
                return [dict(zip(columns, row)) for row in results]
                
        except Exception as e:
            logger.error(f"Error finding all records from {self.table_name}: {e}")
            return []
    
    def find_by_id(self, record_id: Any) -> Optional[Dict[str, Any]]:
        """Find a record by its ID"""
        query = f"SELECT * FROM {self.table_name} WHERE id = %s"
        
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (record_id,))
                result = cursor.fetchone()
                
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, result))
                return None
                
        except Exception as e:
            logger.error(f"Error finding record by ID {record_id} in {self.table_name}: {e}")
            return None
    
    def find_by_field(self, field_name: str, field_value: Any) -> List[Dict[str, Any]]:
        """Find records by a specific field value"""
        query = f"SELECT * FROM {self.table_name} WHERE {field_name} = %s"
        
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (field_value,))
                columns = [desc[0] for desc in cursor.description]
                results = cursor.fetchall()
                
                return [dict(zip(columns, row)) for row in results]
                
        except Exception as e:
            logger.error(f"Error finding records by {field_name}={field_value} in {self.table_name}: {e}")
            return []
    
    def save(self, data: Dict[str, Any]) -> bool:
        """Save a new record to the database"""
        try:
            # Handle different table structures
            if self.table_name == "users":
                return self._save_user(data)
            elif self.table_name == "messages":
                return self._save_message(data)
            else:
                logger.error(f"Unknown table: {self.table_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error saving record to {self.table_name}: {e}")
            return False
    
    def _save_user(self, data: Dict[str, Any]) -> bool:
        """Save user record"""
        query = """
            INSERT INTO users (username, password, role, login_time) 
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        
        login_time = None
        if 'login_time' in data and data['login_time']:
            if isinstance(data['login_time'], str):
                try:
                    login_time = datetime.fromisoformat(data['login_time'])
                except:
                    login_time = None
            else:
                login_time = data['login_time']
        
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (
                    data['username'],
                    data['password'], 
                    data.get('role', 'user'),
                    login_time
                ))
                result = cursor.fetchone()
                return result is not None
                
        except Exception as e:
            logger.error(f"Error saving user: {e}")
            return False
    
    def _save_message(self, data: Dict[str, Any]) -> bool:
        """Save message record"""
        query = """
            INSERT INTO messages (username, sender, text, send_time, is_read) 
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        
        send_time = datetime.now()
        if 'send_time' in data and data['send_time']:
            if isinstance(data['send_time'], str):
                try:
                    send_time = datetime.strptime(data['send_time'], "%Y-%m-%d godz. %H:%M")
                except:
                    pass
        
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (
                    data['username'],
                    data['sender'],
                    data['text'],
                    send_time,
                    data.get('is_read', 0)
                ))
                result = cursor.fetchone()
                return result is not None
                
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return False
    
    def update(self, record_id: Any, data: Dict[str, Any]) -> bool:
        """Update an existing record"""
        if not data:
            return False
            
        # Build dynamic UPDATE query
        set_clauses = []
        values = []
        
        for key, value in data.items():
            set_clauses.append(f"{key} = %s")
            # Handle datetime conversion for specific fields
            if key in ['login_time', 'read_time'] and isinstance(value, str):
                try:
                    if 'godz.' in value:
                        value = datetime.strptime(value, "%Y-%m-%d godz. %H:%M")
                    else:
                        value = datetime.fromisoformat(value)
                except:
                    pass
            values.append(value)
        
        values.append(record_id)  # for WHERE clause
        
        query = f"UPDATE {self.table_name} SET {', '.join(set_clauses)} WHERE id = %s"
        
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query, values)
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error updating record {record_id} in {self.table_name}: {e}")
            return False
    
    def delete(self, record_id: Any) -> bool:
        """Delete a record by its ID"""
        query = f"DELETE FROM {self.table_name} WHERE id = %s"
        
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (record_id,))
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error deleting record {record_id} from {self.table_name}: {e}")
            return False
    
    def count(self) -> int:
        """Count total records in the table"""
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except Exception as e:
            logger.error(f"Error counting records in {self.table_name}: {e}")
            return 0
