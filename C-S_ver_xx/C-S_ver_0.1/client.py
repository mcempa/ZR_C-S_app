import socket as s
from lib import ClientManager

with ClientManager() as client:
    while True:
        client.send_command()
        response = client.recv_response()
        client.print_response(response)   
        if response == "stop" or not response:
            break  # Wyjdź z pętli, jeśli response to "stop"
        