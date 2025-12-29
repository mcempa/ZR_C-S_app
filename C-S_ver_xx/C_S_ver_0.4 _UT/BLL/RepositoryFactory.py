from config import DATABASE_TYPE, PATH_USERS_DB, PATH_MESSAGES_DB, SQL_CONNECTION_STRING
from DAL.base_repository import BaseRepository
from DAL.json_repository import JsonRepository

class RepositoryFactory:
    """Factory for creating repository instances based on configuration"""
    
    @staticmethod
    def create_users_repository() -> BaseRepository:
        """Creates users repository based on DATABASE_TYPE configuration"""
        if DATABASE_TYPE == "JSON":
            return JsonRepository(PATH_USERS_DB, "users")
        elif DATABASE_TYPE == "SQL":
            # Future SQL implementation
            from DAL.sql_repository import SqlRepository
            return SqlRepository(SQL_CONNECTION_STRING, "users")
        else:
            raise ValueError(f"Unsupported database type: {DATABASE_TYPE}")
    
    @staticmethod
    def create_messages_repository() -> BaseRepository:
        """Creates messages repository based on DATABASE_TYPE configuration"""
        if DATABASE_TYPE == "JSON":
            return JsonRepository(PATH_MESSAGES_DB, "messages")
        elif DATABASE_TYPE == "SQL":
            # Future SQL implementation
            from DAL.sql_repository import SqlRepository
            return SqlRepository(SQL_CONNECTION_STRING, "messages")
        else:
            raise ValueError(f"Unsupported database type: {DATABASE_TYPE}")