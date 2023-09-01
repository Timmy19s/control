from customtkinter import (CTk,
                           CTkFrame,
                           CTkProgressBar,
                           CTkLabel,
                           CTkButton,
                           CTkEntry,
                           CTkFont)
from threading import Thread
from time import sleep
import socket

class Frames(CTkFrame):
    def __init__(self, master, name,rows=None, columns=None, height=140):
        super().__init__(master, height=height)
        self.grid_propagate(False) # запретить изменять размер
        
        
        # позволить растягиваться
        if rows != None:
            self.rowconfigure(rows,weight=1)
        if columns != None:
            self.columnconfigure(columns, weight=1)
            
        if name != 'terminal': #Терминал будет всегда открыт
            master.dict_frames[name] = self
        
            
        
        
        
class APP(CTk):
    def __init__(self):
        super().__init__()
        
        self.title("client")
        self.geometry(f"{360}x{420}")
        self.resizable(False, False)
        
        # позволить растягиваться по горизонтали
        self.grid_columnconfigure(0, weight=1)
        
        
        # текст для терминала
        self.queue_mes = []
        self.text_for_term = ''
        
        # шрифт
        self.font = CTkFont('Comic Sans MS', 20, 'bold')
        
        # создать словарь разметок
        self.dict_frames = {}
            
        # терминал
        self.terminal_frame = Frames(self,'terminal' ,0, 0, 220)
        # self.terminal_frame.grid_propagate(False) # запретить изменять размер
        self.terminal_label = CTkLabel(self.terminal_frame, text='Info', font= CTkFont('Comic Sans MS', 24))#, justify = 'left')
        self.terminal_label.grid(row=0,column=0,pady=40,padx=(0,20), sticky = 'ew')
        self.load_bar = CTkProgressBar(self.terminal_frame)
        self.load_bar.grid(row=1,column=0,pady=(0,20),padx=10)
        
        self.terminal_frame.grid(row=0, column=0, pady = 20, padx=30, sticky='we')
        
        # регистрация
        self.regist_frame = Frames(self, 'regist', (0,1),0)
        self.regist_button_add = CTkButton(self.regist_frame, text = 'отправить', font = self.font)
        self.regist_button_add.grid(row=1,column=1,pady=(0,30),padx=20, sticky = 'se')
        self.regist_button_next = CTkButton(self.regist_frame, text = 'дальше', font = self.font)
        self.regist_button_next.grid(row=1,column=0,pady=(0,30),padx=20, sticky = 'se')
        self.regist_entry = CTkEntry(self.regist_frame, placeholder_text='Введите ваше имя', font = self.font)
        self.regist_entry.grid(row=0,column=0,pady=10,padx=20, columnspan=2, sticky = 'we')
        
        # self.regist_frame.grid(row=1, column=0, pady = (0,20), padx=20, sticky='we')
        
        self.no_conn_frame = Frames(self,'no_conn', 0, (0,1))
        self.no_conn_button = CTkButton(self.no_conn_frame, text = 'поменять', font = self.font, command=self.draw_message)
        self.no_conn_button.grid(row=0,column=1,pady=30,padx=20, sticky = 'se')
        self.no_conn_entry = CTkEntry(self.no_conn_frame, placeholder_text='Код', font = self.font, width=60)
        self.no_conn_entry.grid(row=0,column=0,pady=30,padx=20, sticky = 's')
        
        # self.connect_to_server()
        self.change_frame('regist')
     
    def draw_message(self, mes='Приветсвую/Первый вход'):
        def start_draw():
            ind = 0
            
            self.terminal_label.configure(text = '')
            while ind< len(self.queue_mes[0]):
                self.text_for_term += str(self.queue_mes[-1][ind])
                self.terminal_label.configure(text = self.text_for_term)
                sleep(0.03)
                
                ind += 1
                
                if len(self.queue_mes) != 1: # Новое сообщение
                    ind = 0
                    self.queue_mes.pop(0) # удаляю предыдущее
                    self.text_for_term = ''   
            
            self.text_for_term = ''    
            self.queue_mes.pop(0)
                    
        # меняю / на \n и добавляю в список
        self.queue_mes.append(mes.replace('/','\n'))
        if len(self.queue_mes) == 1: # новое сообщение, запускаю цикл
            g = Thread(target=start_draw)
            g.start()

    def connect_to_server(self):
        def data_interchange():
            # получить хост и порт
            with open('HOST_PORT.txt') as file:
                HOST = file.readline()[:-1]
                PORT = int(file.readline()[:-1])
                
            # подключиться к серверу
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # подключение
                self.load_bar.set(0.5)
                self.load_bar.configure(mode='indeterminate')
                self.load_bar.start()
                self.draw_message('Подключение/к серверу')
                try:
                    s.connect((HOST, PORT))
                    s.send(("Hello, world").encode())
                except ConnectionRefusedError:
                    self.draw_message('Сервер/не отвечает:(/Смените код')
                finally:
                    self.load_bar.set(1)
                    self.load_bar.configure(mode='determinate')
                    self.load_bar.stop()
        
        g = Thread(target=data_interchange)
        g.start()

    def change_frame(self, name=None):
        # спрятать все рамки
        for frm in tuple(self.dict_frames.keys()):
            self.dict_frames[frm].grid_forget()
            
        if name != None:
            self.dict_frames[name].grid(row=1, column=0, pady = (0,20), padx=20, sticky='we')
        
app = APP()
app.mainloop()