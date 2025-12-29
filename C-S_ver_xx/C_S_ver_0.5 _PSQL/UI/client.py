import socket as s
import sys
import os
import json

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from BLL.ClientConnectionManager import ClientConnectionManager
from BLL.ClientCommandFactory import ClientCommandFactory
from UI.ClientUIHandler import ClientUIHandler


with ClientConnectionManager() as connection:
    command_factory = ClientCommandFactory()
    ui_handler = ClientUIHandler()
    
    while True:
        try:
            # UI layer handles user interaction
            command = ui_handler.get_command_input()
            
            # Business layer validates command
            if not command_factory.is_valid_command(command):
                ui_handler.show_error("Nieznane polecenie. Spróbuj ponownie.")
                continue
            
            # UI layer gets command parameters
            data_input = ui_handler.get_command_parameters(command)
            
            if command == "logout":
                try:
                    # Utwórz żądanie logout DTO
                    logout_request = command_factory.create_request(command, {})
                    response_dto = connection.send_request(logout_request)
                    ui_handler.show_response(response_dto)
                    if response_dto.success:
                        ui_handler.show_info("Wylogowano pomyślnie")
                except (ConnectionResetError, ConnectionError, TimeoutError) as e:
                    ui_handler.show_error(f"Błąd podczas wylogowywania: {e}")
                except Exception as e:
                    ui_handler.show_error(f"Nieoczekiwany błąd podczas wylogowywania: {e}")
                finally:
                    ui_handler.show_info("Zamykanie programu...")
                    try:
                        connection.close()
                    except Exception as e:
                        ui_handler.show_error(f"Błąd podczas zamykania połączenia: {e}")
                    break
            else:
                try:
                    # Business layer creates request
                    request_dto = command_factory.create_request(command, data_input)
                    
                    #print(f"🔍 DEBUG CLIENT - Request DTO: {request_dto}")
                    
                    # Network layer sends DTO request and receives DTO response
                    response_dto = connection.send_request(request_dto)
                    ui_handler.show_response(response_dto)
                    
                except ConnectionError:
                    ui_handler.show_error("Błąd połączenia z serwerem. Sprawdź połączenie i spróbuj ponownie.")
                    break
                except Exception as e:
                    ui_handler.show_error(f"Wystąpił błąd: {str(e)}")
                    continue
        except KeyboardInterrupt:
            print("Program został przerwany przez użytkownika.")
            connection.close()
            break
        except Exception as e:
            print(f"Wystąpił nieoczekiwany błąd: {str(e)}")
            connection.close()
            continue

    
        

        
