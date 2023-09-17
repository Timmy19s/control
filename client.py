from customtkinter import (CTk,
                           CTkFrame,
                           CTkProgressBar,
                           CTkLabel,
                           CTkButton,
                           CTkEntry,
                           CTkFont,
                           CTkScrollableFrame)
from threading import Thread
from time import sleep
import socket
import ctypes
from pickle import dumps

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
        
from datetime import datetime         
        
        
        
class APP(CTk):
    # список неотслежываемых программ
    with open('lst.txt') as file:
        untraceable_prs = ['',] # пустой процесс тоже есть в списке программ
        for i in file:
            untraceable_prs.append(i[:-1])
    
    def __init__(self):
        super().__init__()
        
        self.title("client")
        self.geometry(f"{360}x{420}")
        self.resizable(False, False)
        
        # позволить растягиваться по горизонтали
        self.grid_columnconfigure(0, weight=1)
        
        
        # для socket
        self.id = ''
        self.has_at_server = False # флаг о том, что есть в базе
        self.controling_flag = False
        self.close_contr = True
        self.queue_comm_text = None
        self.task_server = None
        
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
        self.regist_button_add = CTkButton(self.regist_frame, text = 'отправить', font = self.font, command=self.regist)
        self.regist_button_add.grid(row=1,column=1,pady=(0,30),padx=20, sticky = 'se')
        self.regist_button_next = CTkButton(self.regist_frame, text = 'дальше', font = self.font, command=self.pass_regt)
        self.regist_button_next.grid(row=1,column=0,pady=(0,30),padx=20, sticky = 'se')
        self.regist_entry = CTkEntry(self.regist_frame, placeholder_text='Введите ваше имя', font = self.font)
        self.regist_entry.grid(row=0,column=0,pady=10,padx=20, columnspan=2, sticky = 'we')
        
        # self.regist_frame.grid(row=1, column=0, pady = (0,20), padx=20, sticky='we')
        
        self.no_conn_frame = Frames(self,'no_conn', 0, (0,1))
        self.no_conn_button = CTkButton(self.no_conn_frame, text = 'поменять', font = self.font, command=self.change_host)
        self.no_conn_button.grid(row=0,column=1,pady=30,padx=20, sticky = 'se')
        self.no_conn_entry = CTkEntry(self.no_conn_frame, placeholder_text='Код', font = self.font, width=60)
        self.no_conn_entry.grid(row=0,column=0,pady=30,padx=20, sticky = 's')
        
        self.connect_to_server()
        # self.change_frame('regist')
     
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

    def connect_to_server(self, comm = 'open', data = None):
        def data_interchange(data = data):
            # получить хост и порт
            with open('HOST_PORT.txt') as file:
                HOST = file.readline()[:-1]
                PORT = int(file.readline()[:-1])
                
            # print(date)
                
            # подключиться к серверу
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # подключение
                self.load_bar.set(0.5)
                self.load_bar.configure(mode='indeterminate')
                self.load_bar.start()
                try:
                    
                    self.draw_message('Подключение/к серверу')
                    
                    s.connect((HOST, PORT))
                    
                        
                except ConnectionRefusedError:
                    self.draw_message('Сервер/не отвечает:(')
                    self. controling_flag = False
                    self.change_frame('no_conn')
                
                except TimeoutError:
                    self.draw_message('Кажется, вы указали/неверный код')
                    self. controling_flag = False
                    self.change_frame('no_conn')
                
                except RuntimeError:
                    pass
                
                else:
                    if comm == 'open': #Состояние регистрации
                        # время последнего подключения
                        with open('last_conn.txt') as file:
                            date = file.readline()[:-1]
                            self.id = file.readline()[:-1]
                            
                            s.send(f'open*{date}/{self.id}'.encode())
                            
                            #получаю ответ сервера
                            data = s.recv(1024).decode()
                            if data == '//regist': #нужно регистрироваться
                                self.draw_message('Требуется/регистрация')
                                self.regist_button_next.grid_forget()
                            else:
                                self.draw_message('Вы есть в базе!/Ваше имя может/быть изменено')
                                
                                
                            self.change_frame('regist')
                    
                    elif comm == 'regist': # запрос на регистрацию
                        # определить, регистрация или смена имени
                        data = f"{self.regist_entry.get()}/{self.id if self.regist_button_next.winfo_ismapped() else None}"
                        
                        # отправить запрос на регистрацию
                        s.send(f'regt*{data}'.encode())
                        
                        answer = s.recv(1024).decode()
                        if answer == '//rename': # сервер одобрил смену имени
                            self.draw_message('Вы сменили/имя!')
                            self.has_at_server = True
                            self.change_frame()
                            self.controller()
                        elif answer != '//has': #такого имени нет в списке сервера
                            self.id, date = answer.split('/')
                            # записываю в файл
                            with open('last_conn.txt','w') as file:
                                file.write(f'{date}\n')
                                file.write(f'{self.id}\n')

                            # переход
                            self.draw_message('Вы/зарегестрированы!')
                            self.change_frame()
                            self.has_at_server = True
                            self.controller()
                        else:
                            self.draw_message('Такое имя уже/занято:(')
                    
                    elif comm == 'pass':
                        s.send(f'pass*{self.id}'.encode())
                        self.controller()
                        self.draw_message('Вы прошли!')

                    elif comm == 'control': # клиент отправляет отчет об открытых прогах
                        # отправляю запрос на отправку вместе с id
                        self.draw_message('*****')
                        print(self.id)
                        s.send(f'ctrl*{self.id}'.encode())
                        
                        # получить разрешение
                        answer = (s.recv(1024)).decode()
                        
                        # отправить отчет
                        if answer == '//ok':
                            print(data)
                            s.send(dumps(data))

                        # побочные команды
                        if self.queue_comm_text != None:
                            print(self.queue_comm_text)
                            if self.queue_comm_text == 'cls':
                                with open('last_conn.txt') as file:
                                    date_client = file.readline()[:-1]
                                
                                s.send(f'cls*{date_client}'.encode())
                                # self.queue_comm_text = None
                                print('cls_send')
                        else:
                            s.send(f'0'.encode())
                            
                        
                        # задачи от сервера
                        data = s.recv(1024).decode()
                        if data == 'cls': # надо завершить программу
                            self.task_server = 'task_cls'
                            
                        
                        
                           
                finally:
                    self.load_bar.set(1.0)
                    self.load_bar.configure(mode='determinate')
                    self.load_bar.stop()
                    
                    print(self.queue_comm_text)
                    if self.queue_comm_text == 'cls': # закрыть прогу
                        print('closing')
                        def close():
                            self.destroy()
                        self.after(1000,close)
                    
        

        g = Thread(target=data_interchange)
        g.start()

    def change_frame(self, name=None):
        # спрятать все рамки
        for frm in tuple(self.dict_frames.keys()):
            self.dict_frames[frm].grid_forget()
            
        if name != None:
            self.dict_frames[name].grid(row=1, column=0, pady = (0,20), padx=20, sticky='we')
            
    def regist(self):
        data = self.regist_entry.get()
        if data != '': #пользователь ввел имя
            # имя не должно содержать некоторые знаки
            if '*' not in data and '/' not in data:
                # имя не должно содержать больше 13 символов
                if len(data)<= 13:
                    self.connect_to_server('regist')
                    
                else:
                    self.draw_message('Используйте/не больше 13 знаков')
                
                
            else:
                self.draw_message('Имя содержит/запрещенные знаки!')
                self.regist_entry.delete(0, 'end')
            
            
        else:
            self.draw_message('Введите ваше имя,/пожалуйста!')
            self.regist_entry.focus()
    
    def pass_regt(self):
        self.connect_to_server('pass')
        self.draw_message('Вход успешно/был осуществлен')
        
        self.change_frame()

    def change_host(self):
        code = self.no_conn_entry.get()
        
        if code.isdigit(): # состоит из цифр
            # открываю файл с хостом и портом
            with open('HOST_PORT.txt') as file:
                HOST = file.readline()[:-1]
                PORT = int(file.readline()[:-1]) # порт менять не буду
                
                # ищу индекс последней точки
                ind = HOST.rfind('.')
                HOST = HOST[:ind+1] + code
        
            # меняю хост
            with open('HOST_PORT.txt', 'w') as file:
                for i in (HOST, PORT):
                    file.write(f'{i}\n')
            
            self.change_frame()
            self.connect_to_server()
                
                
            
        else:
            self.draw_message('Используйте/только цифры!')
            self.no_conn_entry.delete(0, 'end')
        
    def controller(self):
        def controling():
            self.controling_flag = True
            self.close_contr = False
            
            # запустить контроль
            EnumWindows = ctypes.windll.user32.EnumWindows
            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
            GetWindowText = ctypes.windll.user32.GetWindowTextW
            GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
            IsWindowVisible = ctypes.windll.user32.IsWindowVisible
            
            def foreach_window(hwnd, lParam):
                if IsWindowVisible(hwnd):
                    length = GetWindowTextLength(hwnd)
                    buff = ctypes.create_unicode_buffer(length + 1)
                    GetWindowText(hwnd, buff, length + 1)
                    titles.append(buff.value)
                return True
                
            while self.controling_flag:
                # отправлять отчет каждые 5 секунд
                sleep(2)
                
                # задача закрыть приложение
                if self.task_server == 'task_cls':
                    self.queue_comm_text = 'cls'
                
                titles = []
                EnumWindows(EnumWindowsProc(foreach_window), 0)
                # заменить  спецсимвол
                titles = [title.replace('\u200b','') for title in titles]
                titles = [title.replace('\\xa0','') for title in titles]
                titles = [title.replace('\xa0','') for title in titles]

                # сделать список уникальным
                titles = list(set(titles))
                
                # удалить из списка определенные процессы
                for title in tuple(titles):
                    if title in APP.untraceable_prs:
                        titles.remove(title)
                # и
                # new_titles = []
                # for title in tuple(titles):
                #     if title.find('-') != -1: 
                #         new_titles.append(title)
                
                # i = dumps()
                
                # создать единную строку
                self.connect_to_server('control', titles)
                
                # закрыть контроллер
                if self.queue_comm_text == 'cls':
                    break
        # запустить только один поток
        if self.controling_flag == False:
            controling_thread = Thread(target=controling)
            controling_thread.start()
    
    def queue_comm(self, comm = 'cls'): # дать команду в очередь
        self.queue_comm_text = comm
            
        
    
    
app = APP()

def on_closing():
    if app.controling_flag:
        app.queue_comm()
    else:
        app.destroy()    

app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()

# app.connect_to_server('close')
# app.controling_flag = False
# if app.has_at_server:
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         # получить хост и порт
#         with open('HOST_PORT.txt') as file:
#             HOST = file.readline()[:-1]
#             PORT = int(file.readline()[:-1])
        
#         with open('last_conn.txt') as file:
#             date = file.readline()[:-1]
#         s.connect((HOST, PORT))
#         s.send(f'cls*{app.id}/{date}'.encode())
    
    
    
    