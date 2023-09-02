import socket
# from datetime import 
import datetime

date = datetime.datetime.today().__str__()


# прочитать порт
with open('PORT.txt') as P:
    PORT = int(P.readline())
    del(P)

dict_clients = {5:'did'}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind(('0.0.0.0', PORT)) #Принимать все
    server.listen(16)
    
    # запускаю цикл на ожидание неоднократных подключений
    while 1:
        conn, addr = server.accept()
        with conn:
            # print(f"Connected by {addr}")
            # while True:
            data = (conn.recv(1024)).decode()
            
            comm, data = data.split('*')
            
            if comm == 'open': #клиент включил прогу и проверяет статус регистрации
                date_client, id = data.split('/')
                id = int(id)
                
                # проверяю, сходится ли время сеанса и сущесвование id в списке
                if date == date_client and id in tuple(dict_clients.keys()):
                    conn.send('//pass'.encode())
                
                else: # запросить зарегистрироваться
                    conn.send('//regist'.encode())
            
            elif comm == 'regt': # пользователь пытается зарегистрироваться или сменить имя
                name, id = data.split('/')
                
                # проверяю существование идентичных имен
                names = [name.upper() for name in dict_clients.values()] # список имен с верхнего регистра. Был замечен баг.
                if name.upper() not in names: # нет

                    if id == 'None': #создаю новое id
                        # генерирую id
                        id = len(dict_clients)
                        conn.send(f'{id}/{date}'.encode())
                        
                        
                        
                    else:
                        id = int(id)
                        
                    # добавляю или меняю
                    dict_clients[id] = name    
                    print(dict_clients)
                        
                else:
                    conn.send('//has'.encode())
                
               
#             print(data)