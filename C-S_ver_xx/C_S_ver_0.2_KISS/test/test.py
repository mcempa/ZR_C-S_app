import pandas as pd
from config import *
# def prepere_request():
#     command = input("Podaj komendę: ")
#     if command:
#         command = command.lower()
#         data_input = input("Podaj dane (oddzielone spacją): ").split()
#         return command, data_input
    
# command, data_input = prepere_request()

# print(command)         #sddsd
# print(*data_input)      #['sdd', 'dsd']

# def test_request(pa1, pa2, pa3):
#     print(pa1)
#     print(pa2)
#     print(pa3)

# data = ("login", {
#             "username": 'gfgf',
#             "password": 'pgfg',
#             "timestamp": 3
#         })

# test_request(data[1].values())

# data =["sdsd", "dsds", "sds"]

# print(data)
# print(*data[0])


#df = pd.read_json(PATH_USERS_DB)
# username = df['users'][0]['username']
# print(username)  # wyświetli: magda
# import json
# with open(PATH_USERS_DB, 'r') as file:
#             users = pd.read_json(file)
#             #print(users['users'])
#             for index, user in users['users']:
#                     print(index)
#                     print(user)
#                     print(users['users'].items())
#                     print (True)
#             print(False)


# command = input("Podaj komendę: ").lower()
# a=''
# print(command)
# if a==command:
#     print(True)
# else:
#     print(False)
import json 
with open(PATH_MESSAGES_DB, 'r') as file:
        data = json.load(file)
print(data)
new_messages = list([msg['text'], msg['sender'], msg['send_time']] for msg in data['messages'] if (msg['username'] == "magda" and msg['is_read'] == 0))
print(new_messages)
response = []
for message in new_messages:
        response.append(f"Od: {message[1]}, Treść: {message[0]}, Wysłano: {message[2]}")
if response:
        print( "\n".join(response))