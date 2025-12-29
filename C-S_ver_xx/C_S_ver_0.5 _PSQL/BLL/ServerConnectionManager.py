import socket as s
from datetime import datetime
from config import *
import json

class ServerConnectionManager():
    def __init__(self):
        self.host = SERVER_CONFIG["host"]
        self.port = SERVER_CONFIG["port"]
        self.max_connections = SERVER_CONFIG["max_connections"]
        self.buffer_size = SERVER_CONFIG["buffer_size"]
        self.server_socket = None
        
    def start_server(self):
        """Uruchomienie serwera z ulepszoną obsługą błędów"""
        try:
            self.server_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
            # Pozwól na ponowne użycie adresu
            self.server_socket.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
            self.server_socket.settimeout(CONNECTION_TIMEOUT)
            
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_connections)
            print(f"Serwer nasłuchuje na {self.host}:{self.port}")
            
        except OSError as e:
            if e.errno == 98:  # Address already in use
                print(f"Port {self.port} jest już zajęty. Spróbuj inny port.")
            else:
                print(f"Błąd systemu operacyjnego: {e}")
            raise ConnectionError(f"Nie można uruchomić serwera: {e}")
        except s.error as e:
            print(f"Błąd socketu podczas uruchamiania serwera: {e}")
            raise s.error(f"Nie można uruchomić serwera: {e}")
        except Exception as e:
            print(f"Nieoczekiwany błąd podczas uruchamiania serwera: {e}")
            raise

    def stop_server(self):
        # Zamknij połączenie
        if self.server_socket:
            self.server_socket.close()
            print("Serwer został zamknięty.")

    def accept_client(self):
        """Akceptowanie klienta z obsługą błędów"""
        if not self.server_socket:
            raise ConnectionError("Serwer nie został uruchomiony")
            
        try:
            client_socket, address = self.server_socket.accept()
            client_socket.settimeout(CONNECTION_TIMEOUT)
            return client_socket, address
            
        except s.timeout:
            # Timeout jest normalny dla nieblokującego serwera
            raise
        except (ConnectionAbortedError, ConnectionResetError) as e:
            print(f"Połączenie przerwane przez klienta: {e}")
            raise ConnectionError(f"Połączenie przerwane: {e}")
        except s.error as e:
            print(f"Błąd socketu podczas akceptowania połączenia: {e}")
            raise s.error(f"Błąd akceptowania: {e}")
        except Exception as e:
            print(f"Nieoczekiwany błąd podczas akceptowania połączenia: {e}")
            raise

    def handle_client(self, client_socket):     
        try:
            data_string = client_socket.recv(self.buffer_size).decode("utf-8")
            
            # DEBUG - co dokładnie otrzymujemy
            print(f"🔍 DEBUG SERVER RECV - Raw data: '{data_string}'")
            print(f"🔍 DEBUG SERVER RECV - Data length: {len(data_string)}")
            print(f"🔍 DEBUG SERVER RECV - Data repr: {repr(data_string)}")
            
            # Walidacja długości danych
            if len(data_string.strip()) == 0:
                print(f"🚨 SERVER - Otrzymano puste dane! Length: {len(data_string)}")
                raise ValueError("Otrzymano puste dane")
            if len(data_string) > MAX_REQUEST_SIZE:
                raise ValueError(f"Dane przekraczają maksymalny rozmiar {MAX_REQUEST_SIZE}")
            
            try:
                # Bezpieczne parsowanie JSON
                parsed_data = json.loads(data_string)
                print(f"🔍 DEBUG SERVER - Parsed JSON: {parsed_data}")
                print(f"🔍 DEBUG SERVER - Type: {type(parsed_data)}")
                
                # Sprawdź format danych - tylko DTO
                if isinstance(parsed_data, dict) and 'command' in parsed_data and 'data' in parsed_data:
                    # Format RequestDTO: {"command": "help", "data": {}}
                    command = parsed_data['command']
                    data = parsed_data.get('data', {})
                    print(f"🔍 DEBUG SERVER - RequestDTO format: command='{command}', data={data}")
                else:
                    raise ValueError("Nieprawidłowa struktura danych - oczekiwano formatu RequestDTO: {\"command\": ..., \"data\": ...}")
                
                # Walidacja komendy
                if not isinstance(command, str) or len(command.strip()) == 0:
                    raise ValueError("Komenda musi być niepustym tekstem")
                if len(command) > MAX_COMMAND_LENGTH:
                    raise ValueError(f"Komenda przekracza maksymalną długość {MAX_COMMAND_LENGTH}")
                
                # Walidacja danych
                if not isinstance(data, dict):
                    raise ValueError("Dane muszą być słownikiem")
                
                # Zwróć w formacie listy dla kompatybilności z resztą kodu
                return [command, data]
                
            except json.JSONDecodeError as e:
                print(f"Błąd podczas parsowania JSON: {e}")
                raise ValueError("Nieprawidłowy format JSON")
            except (ValueError, TypeError) as e:
                print(f"Błąd walidacji danych: {e}")
                raise 
                
        except UnicodeDecodeError as e:
            print(f"Błąd dekodowania danych: {e}")
            raise 
        except s.error as e:
            print(f"Błąd połączenia: {e}")
            raise 

