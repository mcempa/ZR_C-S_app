import socket as s
from services.ClientConnectionManager import ClientConnectionManager
from services.UserClientManager import UserClientManager


with ClientConnectionManager() as connation:
    user_manager = UserClientManager()
    while True:
        try:
            command, data_input = user_manager.prepere_request()
            #print(f"client command: {command}")
            #print(f"client data_input: {data_input}")
            
            if command not in user_manager.command_map:
                print("Nieznane polecenie. Spróbuj ponownie.")
                continue

            if command == "logout":
                try:
                    request = user_manager.command_map[command](command)
                    connation.send_request(str(request)) 
                    connation.recv_response()
                    break
                except Exception as e:
                    print(f"Błąd podczas wylogowywania: {str(e)}")
                    continue

            if command in user_manager.command_map:
                try:
                    if len(data_input) > 0:
                        request = user_manager.command_map[command](command, *data_input) 
                    elif len(data_input) == 0 and command != "logout":
                        request = user_manager.command_map[command](command)
                    #print(request)
                    connation.send_request(str(request)) 
                    connation.recv_response()
                except ConnectionError:
                    print("Błąd połączenia z serwerem. Sprawdź połączenie i spróbuj ponownie.")
                    break
                except Exception as e:
                    print(f"Wystąpił błąd: {str(e)}")
                    continue
        except KeyboardInterrupt:
            print("Program został przerwany przez użytkownika.")
            break
        except Exception as e:
            print(f"Wystąpił nieoczekiwany błąd: {str(e)}")
            continue

    
        

        
