import socket as s
from datetime import datetime
from config import *
import ast

class ServerConnectionManager():
    def __init__(self):
        self.host = SERVER_CONFIG["host"]
        self.port = SERVER_CONFIG["port"]
        self.max_connections = SERVER_CONFIG["max_connections"]
        self.buffer_size = SERVER_CONFIG["buffer_size"]
        self.server_socket = None
        
    def start_server(self):
        try:
            # Utworzenie i konfiguracja socketu
            self.server_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_connections)  # maksymalnie 5 połączeń w kolejce
            print(f"Serwer nasłuchuje na {self.host}:{self.port}")
            
        except s.error as e:
            print(f"Błąd podczas tworzenia serwera: {e}")
            raise

    def stop_server(self):
        # Zamknij połączenie
        if self.server_socket:
            self.server_socket.close()
            print("Serwer został zamknięty.")

    def accept_client(self):
        try:
            return self.server_socket.accept()
            
        except s.error as e:
            print(f"Błąd podczas akceptowania połączenia: {e}")
            raise

    def handle_client(self, client_socket):     
        try:
            data_string = client_socket.recv(1024).decode("utf-8")
            try:
                data_list = ast.literal_eval(data_string)
                return data_list
            except (ValueError, SyntaxError) as e:
                print(f"Błąd podczas parsowania danych: {e}")
                raise 
                
        except UnicodeDecodeError as e:
            print(f"Błąd dekodowania danych: {e}")
            raise 
        except s.error as e:
            print(f"Błąd połączenia: {e}")
            raise 

