import psycopg2
from psycopg2 import sql, DatabaseError, OperationalError
import os
from typing import Optional, Dict, Any
import logging
from contextlib import contextmanager
from config import POSTGRESQL_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgreSQLConnection:
    """PostgreSQL database connection manager for Docker container"""
    
    def __init__(self, 
                 host: str = None,
                 port: int = None,
                 database: str = None,
                 username: str = None,
                 password: str = None):
        
        # Use config values as defaults
        self.connection_params = {
            'host': host or POSTGRESQL_CONFIG['host'],
            'port': port or POSTGRESQL_CONFIG['port'],
            'database': database or POSTGRESQL_CONFIG['database'],
            'user': username or POSTGRESQL_CONFIG['username'],
            'password': password or POSTGRESQL_CONFIG['password'],
            'connect_timeout': 10
        }
        self._connection = None
    
    def connect(self) -> bool:
        """Establish connection to PostgreSQL database"""
        try:
            self._connection = psycopg2.connect(**self.connection_params)
            self._connection.autocommit = True
            logger.info(f"Successfully connected to PostgreSQL database: {self.connection_params['database']}")
            return True
        except OperationalError as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Disconnected from database")
    
    def is_connected(self) -> bool:
        """Check if database connection is active"""
        if not self._connection:
            return False
        try:
            # Test the connection
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except:
            return False
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[list]:
        """Execute SELECT query and return results"""
        if not self.is_connected():
            if not self.connect():
                return None
        
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            return results
        except DatabaseError as e:
            logger.error(f"Database error executing query: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            return None
    
    def execute_command(self, command: str, params: tuple = None) -> bool:
        """Execute INSERT, UPDATE, DELETE command"""
        if not self.is_connected():
            if not self.connect():
                return False
        
        try:
            cursor = self._connection.cursor()
            cursor.execute(command, params)
            cursor.close()
            return True
        except DatabaseError as e:
            logger.error(f"Database error executing command: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error executing command: {e}")
            return False
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor"""
        if not self.is_connected():
            if not self.connect():
                raise DatabaseError("Could not establish database connection")
        
        cursor = self._connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test database connection and return status info"""
        result = {
            'connected': False,
            'database_info': None,
            'tables': [],
            'error': None
        }
        
        try:
            if self.connect():
                result['connected'] = True
                
                # Get database info
                with self.get_cursor() as cursor:
                    cursor.execute("SELECT version();")
                    result['database_info'] = cursor.fetchone()[0]
                    
                    # Get list of tables
                    cursor.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """)
                    result['tables'] = [row[0] for row in cursor.fetchall()]
                    
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Connection test failed: {e}")
        
        return result


# Global database connection instance
_db_connection = None

def get_db_connection() -> PostgreSQLConnection:
    """Get singleton database connection instance"""
    global _db_connection
    if _db_connection is None:
        _db_connection = PostgreSQLConnection()
    return _db_connection

def init_database() -> bool:
    """Initialize database connection"""
    db = get_db_connection()
    return db.connect()

def close_database():
    """Close database connection"""
    global _db_connection
    if _db_connection:
        _db_connection.disconnect()
        _db_connection = None


# Test function
if __name__ == "__main__":
    print("Testing PostgreSQL connection...")
    
    db = PostgreSQLConnection()
    test_result = db.test_connection()
    
    print(f"Connected: {test_result['connected']}")
    if test_result['connected']:
        print(f"Database info: {test_result['database_info']}")
        print(f"Available tables: {test_result['tables']}")
    if test_result['error']:
        print(f"Error: {test_result['error']}")
    
    db.disconnect()
