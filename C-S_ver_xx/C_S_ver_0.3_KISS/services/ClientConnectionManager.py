import socket as s
import time
import os
from datetime import datetime
import json
from config import *

class ClientConnectionManager():
    def __init__(self):
        self.host = SERVER_CONFIG['host']
        self.port = SERVER_CONFIG['port']
    
    def __enter__(self):
        try:
            #Otwórz połączenie
            self.client_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            return self   # !!!!! nie self.client_socket
        
        except ConnectionRefusedError:
            print("Nie można połączyć się z serwerem - serwer nie jest uruchomiony")
            raise
        except Exception as e:
            print(f"Inny błąd podczas wysyłania komendy: {e}")
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        #Zamknij połączenie
        if self.client_socket:
            self.client_socket.close()
            print("Połączenie z serwerem zostaje zamkniete")

    def send_request(self, command):
        try:
            self.client_socket.send(command.encode("utf-8"))
        except ConnectionResetError as e:
            print(f"Błąd połączenia: {e}. Serwer mógł zostać zamknięty.")
            raise
        except Exception as e:
            print(f"Inny błąd podczas wysyłania komendy: {e}")
            raise

    def recv_response(self):
        try:
            response = self.client_socket.recv(1024).decode("utf-8")
            print(response)
            return response
        except ConnectionResetError as e:
            print(f"Błąd połączenia: {e}. Serwer mógł zostać zamknięty.")
            raise   
        except Exception as e:
            print(f"Błąd podczas odbierania odpowiedzi: {e}")
            raise
        