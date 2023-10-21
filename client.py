from customtkinter import (CTk,
                           CTkFrame,
                           CTkProgressBar,
                           CTkLabel,
                           CTkButton,
                           CTkEntry,
                           CTkFont,
                           CTkScrollableFrame,
                           END)
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
    # какая стадия frame
    frame = None
    # список неотслежываемых программ
    with open('lst.txt') as file:
        untraceable_prs = ['',] # пустой процесс тоже есть в списке программ
        for i in file:
            untraceable_prs.append(i[:-1])
    
    # стадия фрейма
    frame_stage = None     
    
    def __init__(self):
        super().__init__()
        
        self.title("client")
        self.geometry(f"{360}x{420}")
        self.resizable(False, False)
        
        # позволить растягиваться по горизонтали
        self.grid_columnconfigure(0, weight=1)
        
        # id и date
        with open('last_conn.txt') as file:
            self.date = file.readline()[:-1]
            self.id = file.readline()[:-1]
            
        # для socket
        self.has_at_server = False # флаг о том, что есть в базе
        self.controling_flag = False
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
        self.regist_entry = CTkEntry(self.regist_frame, font = self.font)
        self.regist_entry.grid(row=0,column=0,pady=10,padx=20, columnspan=2, sticky = 'we')
        
        
        
        # нет подключения
        self.no_conn_frame = Frames(self,'no_conn', 0, (0,1))
        self.no_conn_button = CTkButton(self.no_conn_frame, text = 'поменять', font = self.font, command=self.change_host)
        self.no_conn_button.grid(row=0,column=1,pady=30,padx=20, sticky = 'se')
        self.no_conn_entry = CTkEntry(self.no_conn_frame, placeholder_text='Код', font = self.font, width=60)
        self.no_conn_entry.grid(row=0,column=0,pady=30,padx=20, sticky = 's')
        
        
        
        # Блиц
        self.blitz_frame = Frames(self, 'blitz',0,0)
        self.blitz_button = CTkButton(self.blitz_frame, text = 'Покинуть\nочередь', command= self.blitz) #Встать\nв очередь
        self.blitz_button.grid(row=0, column = 0, pady=20, padx=20, sticky = 'se')
        
        # self.draw_message('Вы можете встать/в очередь')
        # self.draw_message('Вы покинули\nблиц')
        # self.draw_message(f'В {14} в очереди')
        # self.change_frame('blitz')
        

        self.connect_to_server()
     
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

    def blitz(self):
        if self.queue_comm_text != 'cls': # нет задания выйти
            
            if self.blitz_button.cget('text') == 'Встать\nв очередь':
                self.queue_comm_text = 'blz_in'
        
            else:
                self.queue_comm_text = 'blz_out'
    
    def connect_to_server(self, comm = 'open', data = None):
        def data_interchange(s, data = None):
            def send(string):
                s.send(string.encode())
            def recive():
                return (s.recv(1024)).decode()
            
            
            # отправить время и id
            send(f'{self.date}/{self.id}')
            
            # получаю результат
            unswer = recive()
            if unswer == 'rgst': # требуется регистрация   
                if comm == 'regist': # пользователь пытается зарегистрироваться
                    # отправить имя
                    self.focus()
                    send(self.regist_entry.get())
                    
                    # ответ сервера
                    answer = recive()
                    if answer != '//has': #такого имени нет в списке сервера
                        self.id, self.date = answer.split('/')
                        # записываю в файл
                        with open('last_conn.txt','w') as file:
                            file.write(f'{self.date}\n')
                            file.write(f'{self.id}\n')

                        # переход
                        self.draw_message('Вы/зарегестрированы!')
                        self.change_frame()
                        self.has_at_server = True
                        self.controller()
                    else:
                        self.draw_message('Такое имя уже/занято:(')

                else: # пользователь получил задание регистрации
                    send('//ok')
                    self.change_frame('regist')
                    self.regist_entry.delete(0, END)
                    self.regist_entry.configure(placeholder_text='Введите ваше имя')
                    # закрыть контроллер
                    self.controling_flag = False
                    
                    
                    # регистрация
                    self.draw_message('Требуется/регистрация!')
                    
            elif comm == 'open': # если клиент вернулся в базу
                self.draw_message('Вы вернулись!')
                
                # отправляю отчет
                send('/bck')
                recive()

                self.change_frame()
                self.has_at_server = True
                self.controller()
                  
            else: # другие случаи
                # отправляю отчет
                send('/cnt')
                recive()
                
                
                # отправляю отчет
                self.draw_message('*****')
                s.send(dumps(data))


                # получить next
                recive()


                # действия клиента
                # region
                if self.queue_comm_text != None:
                    send(self.queue_comm_text)
                    
                    
                else:
                    send('0')
                # endregion  
                
                
                # стадия сервера
                #region
                data = s.recv(1024).decode()
                if data == 'cls': # надо завершить программу
                    self.task_server = 'task_cls'
                elif 'blz' in data:
                    d, id = data.split('/')
                    
                    # при надобности развернуть рамку
                    if self.blitz_frame.winfo_ismapped() == 0:
                        self.change_frame('blitz')
                    
                    
                    # есть ли в базе
                    if id != '0':
                        self.draw_message(f'Вы {id}\nв очереди!')
                        
                        if self.blitz_button.cget('text') != 'Покинуть\nочередь':
                            self.blitz_button.configure(text = 'Покинуть\nочередь')
                    else:
                        self.draw_message('Вы можете\nвстать в очередь')
                        
                        if self.blitz_button.cget('text') != 'Встать\nв очередь':
                            self.blitz_button.configure(text = 'Встать\nв очередь')
                else:
                    if APP.frame != None:
                        self.change_frame()
                    
                    # очистить стадию при надобности
                    if self.queue_comm_text != None:
                        self.queue_comm_text =  None
                # endregion
        
        def connection(data = data):
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
                    data_interchange(s, data)        
                        
                        
                           
                finally:
                    self.load_bar.set(1.0)
                    self.load_bar.configure(mode='determinate')
                    self.load_bar.stop()
                    
                    if self.queue_comm_text == 'cls': # закрыть прогу
                        def close():
                            self.destroy()
                        self.after(1000,close)
                    
        

        g = Thread(target=connection)
        g.start()

    def change_frame(self, name=None):
        # спрятать все рамки
        for frm in tuple(self.dict_frames.keys()):
            self.dict_frames[frm].grid_forget()
            
        if name != None:
            self.dict_frames[name].grid(row=1, column=0, pady = (0,20), padx=20, sticky='we')
            self.focus()
            
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
            if len(code) < 4: # максимум 3-значное число
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
                self.draw_message('Код должен содержать\nмаксимум 3 знака!')
                self.no_conn_entry.delete(0, 'end')
                self.focus()
                
                
            
        else:
            self.draw_message('Используйте/только цифры!')
            self.no_conn_entry.delete(0, 'end')
            self.focus()
        
    def controller(self):
        def controling():
            self.controling_flag = True
            
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
                sleep(5)
                
                # спустя 5 секунд проверить флаг
                if self.controling_flag == False:
                    break
                
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
    
    
    
    