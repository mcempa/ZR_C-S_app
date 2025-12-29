from BLL.ServerConnectionManager import ServerConnectionManager
from BLL.DbManager import DbManager
from BLL.ServerMessageManager import ServerMessageManager
import socket as s


# po zmnknięciu połączenia z klientemserwer czeka na nowe połączenie
# Zredygnowano z  Menedżer kontekstu (with),  który 
# automatycznie zamyka połączenie po wyjściu z bloku, 
# co nie jest pożądane w przypadku serwera, który powinien działać ciągle.

server = ServerConnectionManager()
server.start_server()

try:
    while True:  # Główna pętla serwera
        client_socket, address = server.accept_client()
        print(f"Połączono z klientem: {address}")
        user_manager = ServerMessageManager()
        
        try:
            while True:  # Pętla obsługi pojedynczego klienta
                request = server.handle_client(client_socket)
                if not request: # Jeśli nie ma danych, bo połączenie zostało przerwane
                    break
                    
                command = request[0]
                data_input = request[1] 
                print(request)
                print(command)
                print(data_input) 
                if not command:  # Sprawdzenie czy komenda nie jest pusta
                    continue
                
                if command == "logout":
                    print(f"Klient {address} się wylogował")
                    break  # Przerywa tylko wewnętrzną pętlę
                
                if command in user_manager.command_map:
                    if len(data_input) > 0:
                        response = str(user_manager.command_map[command](command, *data_input.values()))
                    else:
                        response = str(user_manager.command_map[command](command))
                    client_socket.send(response.encode("utf-8"))
                         
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
        