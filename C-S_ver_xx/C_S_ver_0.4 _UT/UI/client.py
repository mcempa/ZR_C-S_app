import socket as s
from BLL.ClientConnectionManager import ClientConnectionManager
from BLL.ClientMessageManager import ClientMessageManager


with ClientConnectionManager() as connection:
    user_manager = ClientMessageManager()
    while True:
        try:
            command, data_input = user_manager.prepare_request_interactive()
            #print(f"client command: {command}")
            #print(f"client data_input: {data_input}")
            
            if command not in user_manager.command_map:
                print("Nieznane polecenie. Spróbuj ponownie.")
                continue

            if command == "logout":
                try:
                    connection.send_request("logout")
                    response = connection.recv_response()
                    print(f"response: {response}")
                    if response == "OK":
                        print("Wylogowano pomyślnie")
                except (ConnectionResetError, ConnectionError, TimeoutError) as e:
                    print(f"Błąd podczas wylogowywania: {e}")
                except Exception as e:
                    print(f"Nieoczekiwany błąd podczas wylogowywania: {e}")
                finally:
                    print("Zamykanie programu...")
                    try:
                        connection.close()
                    except Exception as e:
                        print(f"Błąd podczas zamykania połączenia: {e}")
                    break
            else:
                try:
                    if len(data_input) > 0:
                        request = user_manager.command_map[command](command, **data_input) 
                    else:
                        request = user_manager.command_map[command](command)
                    #print(request)
                    connection.send_request(str(request)) 
                    connection.recv_response()
                except ConnectionError:
                    print("Błąd połączenia z serwerem. Sprawdź połączenie i spróbuj ponownie.")
                    break
                except Exception as e:
                    print(f"Wystąpił błąd: {str(e)}")
                    continue
        except KeyboardInterrupt:
            print("Program został przerwany przez użytkownika.")
            connection.close()
            break
        except Exception as e:
            print(f"Wystąpił nieoczekiwany błąd: {str(e)}")
            connection.close()
            continue

    
        

        
