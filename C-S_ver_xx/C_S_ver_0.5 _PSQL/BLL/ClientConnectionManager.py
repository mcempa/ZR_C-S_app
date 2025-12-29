import socket as s
import time
import os
from datetime import datetime
import json
from config import *
from Models.MessageProtocol import RequestDTO, ResponseDTO

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
            
    def send_request(self, request_dto: RequestDTO) -> ResponseDTO:
        """Wysyła żądanie DTO i odbiera odpowiedź DTO"""
        try:
            # Serializuj żądanie do JSON
            json_request = request_dto.to_json()
            #print(f"🔍 DEBUG CLIENT - Sending DTO: {json_request}")
            
            # Walidacja przed wysłaniem
            if not json_request or len(json_request.strip()) == 0:
                raise ValueError("Pusty JSON request")
            if len(json_request.encode('utf-8')) > MAX_REQUEST_SIZE:
                raise ValueError(f"Request przekracza maksymalny rozmiar {MAX_REQUEST_SIZE}")
            
            # Wyślij żądanie
            bytes_to_send = json_request.encode("utf-8")
            self.client_socket.send(bytes_to_send)
            
            # Odbierz odpowiedź
            response_bytes = self.client_socket.recv(SERVER_CONFIG["buffer_size"])
            if not response_bytes:
                raise ConnectionError("Serwer zamknął połączenie")
            json_response = response_bytes.decode("utf-8")
            #print(f"🔍 DEBUG CLIENT - Received response: {json_response}")
            
            # Deserializuj odpowiedź z JSON
            response_dto = ResponseDTO.from_json(json_response)
            return response_dto
            
        except json.JSONDecodeError as e:
            print(f"Błąd parsowania JSON: {e}")
            # Zwróć błędną odpowiedź DTO
            return ResponseDTO.error_response(
                f"Błąd parsowania odpowiedzi serwera: {e}",
                "JSON_PARSE_ERROR"
            )
        except Exception as e:
            print(f"Błąd podczas komunikacji: {e}")
            return ResponseDTO.error_response(
                f"Błąd komunikacji: {e}",
                "COMMUNICATION_ERROR"
            )
    
    def close(self):
        """Bezpieczne zamknięcie połączenia"""
        try:
            if hasattr(self, 'client_socket') and self.client_socket:
                self.client_socket.close()
                print("Połączenie zostało zamknięte")
        except Exception as e:
            print(f"Błąd podczas zamykania połączenia: {e}")
        