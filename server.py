import socket
from threading import Thread
import datetime
from customtkinter import (CTk,
                           CTkFrame,
                           CTkProgressBar,
                           CTkLabel,
                           CTkButton,
                           CTkEntry,
                           CTkFont,
                           CTkSegmentedButton,
                           CTkImage)
from PIL import Image


class APP(CTk):
    def __init__(self):
        super().__init__()
        
        # окно
        self.title("server")
        self.geometry(f"{int(self.winfo_screenwidth()*0.9)}x{int(self.winfo_screenheight()*0.9)}+0+0")
        
        
        
        # позволить растягиваться
        self.grid_columnconfigure(1,weight=8)
        self.grid_columnconfigure((0,2),weight=1)
        self.grid_rowconfigure(1,weight=1)
        
        
        
        # панель задач
        self.menu_tab = CTkSegmentedButton(self, height=40, values= ('Главное меню',
                                                          'Блиц режим',
                                                          'Голосование',
                                                          'Обмен файлами'))
        self.menu_tab.set('Главное меню')
        self.menu_tab.grid(row=0,column=0, columnspan = 2, sticky = 'nwe')
        
        
        
        # статистика_все
        self.statistic_all_frame = CTkFrame(self)
        self.statistic_all_frame.grid_columnconfigure(0,weight=1)
        self.statistic_all_frame.grid_rowconfigure(2,weight=1)
        self.statistic_all_pie = CTkLabel(self.statistic_all_frame, 
                                          text='Все студенты', 
                                          compound='bottom', 
                                          font=CTkFont(size=16, weight="bold"))
        self.statistic_all_pie.grid(row=0, column = 0, pady =20,  sticky = 'ew')
        self.statistic_all_title = CTkLabel(self.statistic_all_frame, text= 'Новые процессы:')
        self.statistic_all_title.grid(row=1, column = 0)
        self.statistic_all_list = CTkLabel(self.statistic_all_frame, text='Visual studio code\ndd\n\ndd\nse')
        self.statistic_all_list.grid(row=2, column = 0,pady = 10, sticky = 'nwe')
        self.statistic_all_button = CTkButton(self.statistic_all_frame, text = 'закрыть все\nзапрещенные процессы')
        self.statistic_all_button.grid(row=3, column = 0, sticky = 'swe')
        
        
        self.statistic_all_frame.grid(row = 0,column = 2, rowspan = 3, sticky = 'nsew')
        
        
        
        # статистика_Определенный человек
        self.statistic_persenal_frame = CTkFrame(self)
        self.statistic_persenal_frame.grid_columnconfigure(0,weight=1)
        self.statistic_persenal_frame.grid_rowconfigure(2,weight=1)
        self.statistic_persenal_pie = CTkLabel(self.statistic_persenal_frame, text='Name', compound='bottom')
        self.statistic_persenal_pie.grid(row=0, column = 0, pady =20,  sticky = 'ew')
        self.statistic_persenal_title = CTkLabel(self.statistic_persenal_frame, text= 'Новые процессы:')
        self.statistic_persenal_title.grid(row=1, column = 0)
        self.statistic_persenal_list = CTkLabel(self.statistic_persenal_frame, text='Visual studio code\ndd\n\ndd\nse')
        self.statistic_persenal_list.grid(row=2, column = 0,pady = 10, sticky = 'nwe')
        self.statistic_persenal_button = CTkButton(self.statistic_persenal_frame, text = 'Показать\nплохиша')
        self.statistic_persenal_button.grid(row=3, column = 0, sticky = 'swe')
        
        self.statistic_persenal_frame.grid(row = 1,column = 0, rowspan = 2, padx = (0,0), sticky = 'nsew')
        
        
        
        # клиенты
        self.clients_frame = CTkFrame(self, fg_color="transparent")
        # позволить растягиваться
        self.clients_frame.grid_rowconfigure((0,1,2,3), weight=1)
        self.clients_frame.grid_columnconfigure((0,1,2,3), weight=1)
        # создать кнопки для всех клиентов
        self.dict_clients_buttons = {} # кнопки по id
        for i in range(16):
            # создать
            self.dict_clients_buttons[i] = CTkButton(self.clients_frame, 
                                                     text=f'client_{i}', 
                                                     font = CTkFont('Comic Sans MS', 32, 'bold'), 
                                                     fg_color="#dcdcdc", 
                                                     text_color = '#4c4f4c')
            # расположить
            row = i//4
            col = i%4
            self.dict_clients_buttons[i].grid(row=row,column=col)
        self.clients_frame.grid(row=1,column=1, sticky='nsew')    
        
        
        
        # добавить процесс в список
        self.add_process_frame = CTkFrame(self, height=80, fg_color="transparent")
        self.add_process_frame.columnconfigure(0,weight=1)
        self.add_process_entry = CTkEntry(self.add_process_frame, placeholder_text='Добавить процесс')
        self.add_process_entry.grid(row = 0, column = 0, sticky = 'we')
        self.add_process_bott_good = CTkButton(self.add_process_frame, text='В разрешенную\nкатегорию', command=self.draw_pie_all)
        self.add_process_bott_good.grid(row=0, column=1)
        self.add_process_bott_neut = CTkButton(self.add_process_frame, text='В нейтральную\nкатегорию')
        self.add_process_bott_neut.grid(row=0, column=2)
        self.add_process_bott_bad = CTkButton(self.add_process_frame, text='В запрещенную\nкатегорию')
        self.add_process_bott_bad.grid(row=0, column=3)
        self.add_process_frame.grid(row = 2,column = 1, sticky = 'nsew')
        
    def draw_pie_all(self):
        # расширение экрана
        w = self.winfo_width()
        w = int(w*0.1)
        w = 150 if w < 150 else w
        
        # обрезаю по стандарту
        pie = Image.open('ddd.png') 
        pie = pie.crop((226,72,764,618)) 
        
        
        pie = CTkImage(pie, size=(w,w))
        self.statistic_all_pie.configure(image=pie)
        
        # pie = CTkImage(pie, size=(w,w))
        self.statistic_persenal_pie.configure(image=pie)
        
        
        
        
        
        



def start_server():
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
                            conn.send(f'//rename'.encode())
                            id = int(id)
                            
                        # добавляю или меняю
                        dict_clients[id] = name    
                        print(dict_clients)
                            
                    else:
                        conn.send('//has'.encode())
                
    
app = APP()
app.mainloop()          
#             print(data)