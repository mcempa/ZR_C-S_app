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
        return self._connect_with_retry()
    
    def _connect_with_retry(self):
        """Nawiązanie połączenia z mechanizmem ponawiania"""
        last_exception = None
        
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                print(f"Próba połączenia {attempt + 1}/{MAX_RETRY_ATTEMPTS}")
                self.client_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
                self.client_socket.settimeout(CONNECTION_TIMEOUT)
                self.client_socket.connect((self.host, self.port))
                print(f"Połączenie nawiązane pomyślnie")
                return self
                
            except (ConnectionRefusedError, s.timeout, s.error) as e:
                last_exception = e
                print(f"Próba {attempt + 1} nieudana: {e}")
                
                if hasattr(self, 'client_socket') and self.client_socket:
                    self.client_socket.close()
                
                if attempt < MAX_RETRY_ATTEMPTS - 1:
                    print(f"Oczekiwanie {RETRY_DELAY}s przed kolejną próbą...")
                    time.sleep(RETRY_DELAY)
                    
            except Exception as e:
                print(f"Nieoczekiwany błąd podczas połączenia: {e}")
                if hasattr(self, 'client_socket') and self.client_socket:
                    self.client_socket.close()
                raise
        
        print(f"Nie udało się nawiązać połączenia po {MAX_RETRY_ATTEMPTS} próbach")
        raise ConnectionError(f"Połączenie nieudane: {last_exception}")

    def __exit__(self, exc_type, exc_value, traceback):
        #Zamknij połączenie
        if self.client_socket:
            self.client_socket.close()
            print("Połączenie z serwerem zostaje zamkniete")

    def send_request(self, command):
        """Wysłanie żądania z obsługą błędów sieciowych"""
        if not hasattr(self, 'client_socket') or not self.client_socket:
            raise ConnectionError("Brak aktywnego połączenia")
            
        try:
            # Walidacja danych przed wysłaniem
            if not command or len(command.strip()) == 0:
                raise ValueError("Komenda nie może być pusta")
            if len(command.encode('utf-8')) > MAX_REQUEST_SIZE:
                raise ValueError(f"Komenda przekracza maksymalny rozmiar {MAX_REQUEST_SIZE}")
                
            self.client_socket.send(command.encode("utf-8"))
            
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
            print(f"Połączenie zostało przerwane: {e}")
            raise ConnectionError(f"Połączenie przerwane: {e}")
        except s.timeout as e:
            print(f"Przekroczono limit czasu podczas wysyłania: {e}")
            raise TimeoutError(f"Timeout podczas wysyłania: {e}")
        except s.error as e:
            print(f"Błąd socketu podczas wysyłania: {e}")
            raise ConnectionError(f"Błąd sieci: {e}")
        except Exception as e:
            print(f"Nieoczekiwany błąd podczas wysyłania: {e}")
            raise

    def recv_response(self):
        """Odbieranie odpowiedzi z obsługą błędów sieciowych"""
        if not hasattr(self, 'client_socket') or not self.client_socket:
            raise ConnectionError("Brak aktywnego połączenia")
            
        try:
            response = self.client_socket.recv(SERVER_CONFIG["buffer_size"]).decode("utf-8")
            
            if not response:
                raise ConnectionError("Serwer zamknął połączenie")
                
            print(response)
            return response
            
        except (ConnectionResetError, ConnectionAbortedError) as e:
            print(f"Połączenie zostało przerwane przez serwer: {e}")
            raise ConnectionError(f"Połączenie przerwane: {e}")
        except s.timeout as e:
            print(f"Przekroczono limit czasu podczas odbierania: {e}")
            raise TimeoutError(f"Timeout podczas odbierania: {e}")
        except UnicodeDecodeError as e:
            print(f"Błąd dekodowania odpowiedzi: {e}")
            raise ValueError(f"Nieprawidłowe kodowanie odpowiedzi: {e}")
        except s.error as e:
            print(f"Błąd socketu podczas odbierania: {e}")
            raise ConnectionError(f"Błąd sieci: {e}")
        except Exception as e:
            print(f"Nieoczekiwany błąd podczas odbierania: {e}")
            raise
            
    def close(self):
        """Bezpieczne zamknięcie połączenia"""
        try:
            if hasattr(self, 'client_socket') and self.client_socket:
                self.client_socket.close()
                print("Połączenie zostało zamknięte")
        except Exception as e:
            print(f"Błąd podczas zamykania połączenia: {e}")
        