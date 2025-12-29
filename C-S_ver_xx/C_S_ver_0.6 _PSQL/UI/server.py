import sys
import os
import json

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from BLL.ServerConnectionManager import ServerConnectionManager
from BLL.ServerCommandFactory import ServerCommandFactory
from Models.MessageProtocol import RequestDTO, ResponseDTO, MessageProtocol
import socket as s


# Serwer oczekuje na nowe połączenie po zamknięciu połączenia z klientem
# Zrezygnowano z menedżera kontekstu (with), który automatycznie zamyka połączenie
# po wyjściu z bloku, co nie jest pożądane w przypadku serwera, który powinien działać ciągle.

server = ServerConnectionManager()
server.start_server()

try:
    while True:  # Główna pętla serwera
        client_socket, address = server.accept_client()
        print(f"Połączono z klientem: {address}")
        user_manager = ServerCommandFactory()
        
        try:
            while True:  # Pętla obsługi pojedynczego klienta
                raw_request = server.handle_client(client_socket)
                if not raw_request: # Jeśli nie ma danych, bo połączenie zostało przerwane
                    break
                
                try:
                    # raw_request jest zawsze listą z ServerConnectionManager [command, data]
                    command, data = raw_request[0], raw_request[1]
                    
                    # Utwórz RequestDTO z otrzymanych danych
                    request_dto = RequestDTO(command=command, data=data)
                    print(f"🔍 DEBUG SERVER - Parsed DTO: {request_dto}")
                    
                    # Specjalna obsługa logout
                    if request_dto.command == "logout":
                        response_dto = MessageProtocol.create_success_response("OK")
                        print(f"Klient {address} się wylogował")
                        client_socket.send(response_dto.to_json().encode("utf-8"))
                        break
                    
                    # Przetwórz żądanie przez CommandFactory
                    response_dto = user_manager.process_request(request_dto)
                    print(f"🔍 DEBUG SERVER - Response DTO: {response_dto}")
                    
                    # Wyślij odpowiedź DTO jako JSON
                    client_socket.send(response_dto.to_json().encode("utf-8"))
                            
                except json.JSONDecodeError as e:
                    print(f"Błąd parsowania JSON: {e}")
                    error_dto = MessageProtocol.create_error_response("Błąd parsowania żądania", "JSON_PARSE_ERROR")
                    client_socket.send(error_dto.to_json().encode("utf-8"))
                except Exception as e:
                    print(f"Błąd przetwarzania żądania: {e}")
                    error_dto = MessageProtocol.create_error_response(f"Błąd serwera: {str(e)}", "SERVER_ERROR")
                    client_socket.send(error_dto.to_json().encode("utf-8"))
                         
        except Exception as e:
            print(f"Błąd podczas obsługi klienta {address}: {e}")
        finally:
            client_socket.close()
            print(f"Zamknięto połączenie z klientem {address}")
            
except KeyboardInterrupt:
    print("\nZamykanie serwera...")
except Exception as e:
    print(f"Błąd krytyczny serwera: {e}")
finally:
    server.stop_server()    
        