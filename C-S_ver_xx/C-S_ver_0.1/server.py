from lib import ServerManager
from lib import DbManager
import socket as s


with ServerManager() as server:
    try:
        #print(f"server : {server}") # server to instancja klasy ServerManager
        client_socket, adress = server.server_socket.accept()  # metoda accept musi działać na sokecie dlatego jest server_socket
        db = DbManager()

        while True:
            try:
                command = client_socket.recv(1024).decode("utf-8")
                if command == "stop": 
                    response =  server.stop_client(client_socket) # te metody działa na instancji klasy Server_Manager
                    client_socket.send(response.encode("utf-8"))
                    break 
                elif command in server.command_map: 
                    response = server.command_map[command]()
                else:
                    response =  server.get_message()
                #print(command)
                db.add_record (response)  
                client_socket.send(response.encode("utf-8"))

            except ConnectionResetError:
                print("Klient nieoczekiwanie zakończył połączenie")
                break

            except Exception as e:
                print(f"Błąd podczas obsługi klienta: {e}")
                break

    except Exception as e:
        print(f"Błąd podczas akceptowania połączenia: {e}")    
        