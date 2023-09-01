import socket


# прочитать хост и порт
with open('PORT.txt') as P:
    PORT = int(P.readline())
    del(P)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind(('0.0.0.0', PORT)) #Принимать все
    server.listen(16)
    
    conn, addr = server.accept()
    
    
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = (conn.recv(1024)).decode()
            
            
            print(data)