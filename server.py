# Version - v0.91
serv_version = 'v0.91'

import socket
from threading import Thread, active_count
import datetime
from time import sleep, time
from customtkinter import (CTk,
                           CTkFrame,
                           CTkProgressBar,
                           CTkLabel,
                           CTkButton,
                           CTkEntry,
                           CTkFont,
                           CTkSegmentedButton,
                           CTkImage,
                           CTkTextbox,
                           CTkTabview,
                           END)
from PIL import Image
from pickle import loads
import sqlite3
from random import randint


class Button_cl(CTkButton):
    def __init__(self, master, id, text):
        self.id = id
        super().__init__(master.clients_frame, 
                         text='',
                         font = CTkFont('Comic Sans MS', 32, 'bold'),
                         fg_color='#dcdcdc',
                         height=50,
                         command= lambda: master.change_focus(self.id))    
                                        
        
        
        
class APP(CTk):
    run_server = True
    
    # словарь id - процессы
    focus_pers = None
    dict_cntr = {}
    dict_clients = {}
    
    
    # Создаем подключение к базе данных (файл my_database.db будет создан)
    connection = sqlite3.connect('Basedata.db')
    cursor = connection.cursor()
    
    # база данных
    cursor.execute('DELETE FROM PS',)
    # хорошие и плохие процессы
    cursor.execute('SELECT key_word FROM KW WHERE type LIKE "bd"',)
    bad_pr = tuple([i[0] for i in cursor.fetchall()])
    cursor.execute('SELECT key_word FROM KW WHERE type LIKE "gd"',)
    good_pr = tuple([i[0] for i in cursor.fetchall()])
    
    
    # очередь
    queue = []
    
    def __init__(self):
        super().__init__()
        
        # окно
        self.title(f"server ({serv_version})")
        self.geometry(f"{int(self.winfo_screenwidth()*0.9)}x{int(self.winfo_screenheight()*0.5)}+0+0")
        
        
        
        # позволить растягиваться
        self.grid_columnconfigure(1,weight=1)
        # self.grid_columnconfigure((0,2),weight=1)
        self.grid_rowconfigure(2,weight=1)
        
        
        
        # панель задач
        self.menu_tab = CTkSegmentedButton(self, height=40, values= ('Главный экран',
                                                          'Блиц режим',
                                                          'Голосование',
                                                          'Обмен файлами',
                                                          'Отключить подключения'),
                                           command=self.menu_action)
        self.menu_tab.set('Главный экран')
        self.menu_tab.grid(row=0,column=0, columnspan = 2, sticky = 'nwe')
        
        
        
        # терминал
        self.queue_mes = []
        
        self.terminal_frame = CTkFrame(self, height=80)
        self.terminal_frame.columnconfigure(0,weight=1)
        self.terminal_label = CTkLabel(self.terminal_frame, text='Info', font= CTkFont('Comic Sans MS', 32))
        self.terminal_label.grid(row=0,column=0,pady=20,padx=30, sticky = 'w')
        
        self.terminal_frame.grid(row=1,column=1, pady=10, padx=20, sticky='new')
        
        
        
        # статистика_все
        self.statistic_all_frame = CTkFrame(self)
        self.statistic_all_frame.grid_columnconfigure(0,weight=1)
        self.statistic_all_frame.grid_rowconfigure(2,weight=1)
        # 
        # диаграммы
        self.statistic_all_diag_frame = CTkFrame(self.statistic_all_frame, height=180)
        self.statistic_all_diag_frame.rowconfigure(1,weight=1)
        self.statistic_all_diag_frame.columnconfigure((0,1,2),weight=1)
        self.statistic_all_diag_frame.grid_propagate(False)
        self.statistic_all_diag_text = CTkLabel(self.statistic_all_diag_frame, # Надпись
                                                text = 'Все студенты:', 
                                                font= CTkFont('Comic Sans MS', 18))
        self.statistic_all_diag_text.grid(row=0, column=0, columnspan=3)
        self.statistic_all_diag_g = CTkLabel(self.statistic_all_diag_frame, fg_color= '#32cd32', width=50, text = '0%') # зеленная дигр-ма
        self.statistic_all_diag_g.grid(row=1, column=0, sticky = 's')
        self.statistic_all_diag_y = CTkLabel(self.statistic_all_diag_frame, fg_color= '#edff21', width=50, text = '0%') # желтая дигр-ма
        self.statistic_all_diag_y.grid(row=1, column=1, sticky = 's')
        self.statistic_all_diag_r = CTkLabel(self.statistic_all_diag_frame, fg_color= '#ff5029', width=50, text = '0%') # красная дигр-ма
        self.statistic_all_diag_r.grid(row=1, column=2, sticky = 's')
        self.statistic_all_diag_frame.grid(row=0, column = 0)
        # список и кнопка
        self.statistic_all_title = CTkLabel(self.statistic_all_frame, text= 'Новые процессы:', font= CTkFont('Comic Sans MS', 18))
        self.statistic_all_title.grid(row=1, column = 0, pady = (10,0), sticky = 's')
        self.statistic_all_list = CTkTextbox(self.statistic_all_frame)
        self.statistic_all_list.grid(row=2, column = 0,pady = (0,10), padx = 20, sticky = 'nswe')
        self.statistic_all_button = CTkButton(self.statistic_all_frame, text = 'Очистить\nполе', command=self.clean_list_prs)
        self.statistic_all_button.grid(row=3, column = 0, pady=(0,12), sticky = 's')
        
        
        self.statistic_all_frame.grid(row = 0,column = 2, rowspan = 4, sticky = 'nsew')
        
        
        
        # статистика_Определенный человек
        self.statistic_persenal_frame = CTkFrame(self)
        self.statistic_persenal_frame.grid_columnconfigure(0,weight=1)
        self.statistic_persenal_frame.grid_rowconfigure(2,weight=1)
        self.statistic_persenal_title = CTkLabel(self.statistic_persenal_frame, text='Name\nПроцессы:', 
                                                 compound='bottom',
                                                 font= CTkFont('Comic Sans MS', 20))
        self.statistic_persenal_title.grid(row=0, column = 0, pady =(20,0),  sticky = 'ew')
        # рамка процессы
        self.statistic_persenal_list_frame = CTkFrame(self.statistic_persenal_frame, fg_color='transparent')
        self.statistic_persenal_list_frame.columnconfigure(0, weight=1)
        self.statistic_persenal_list_r = CTkLabel(self.statistic_persenal_list_frame, # красные процессы
                                                  fg_color='#ff7a5c',
                                                  corner_radius=10)
        self.statistic_persenal_list_r.grid(row=0, column = 0, padx=10, pady = (10,0), sticky = 'we')
        self.statistic_persenal_list_y = CTkLabel(self.statistic_persenal_list_frame, #желтые
                                                  fg_color='#ffff66',
                                                  corner_radius=10)
        self.statistic_persenal_list_y.grid(row=1, column = 0, padx=10, pady = (10,0), sticky = 'we')
        self.statistic_persenal_list_g = CTkLabel(self.statistic_persenal_list_frame, # зеленые
                                                  fg_color='#66ff66',
                                                  corner_radius=10)
        self.statistic_persenal_list_g.grid(row=2, column = 0, padx=10, pady = (10,0), sticky = 'we')
        self.statistic_persenal_list_frame.grid(row=1, column = 0,pady = 10, sticky = 'nswe')
        self.statistic_persenal_ch_name_entry = CTkEntry(self.statistic_persenal_frame, placeholder_text='Новое имя')
        self.statistic_persenal_change_name = CTkButton(self.statistic_persenal_frame, text = 'Изменить\nимя', command=self.change_name)
        self.statistic_persenal_change_name.grid(row=3, column = 0,pady = (0,10), sticky = 's')
        self.statistic_persenal_button = CTkButton(self.statistic_persenal_frame, text = 'Показать\nплохиша', command=self.show_worst_cl)
        self.statistic_persenal_button.grid(row=4, column = 0, pady=(0,12), sticky = 's')
        
        self.statistic_persenal_frame.grid(row = 1,column = 0, rowspan = 3, padx = (0,0), sticky = 'nsew')
        
        
        # клиенты
        self.clients_frame = CTkFrame(self, fg_color="transparent")
        self.clients_frame.grid_rowconfigure((0,1,2,3), weight=1) # позволить растягиваться
        self.clients_frame.grid_columnconfigure((0,1,2,3), weight=1)
        # создать кнопки для всех клиентов
        self.dict_clients_buttons = {} # кнопки по id
        for i in range(16):
            # создать
            self.dict_clients_buttons[i] = Button_cl(self,i,'fwfwf')
            # расположить
            row = i//4
            col = i%4
            self.dict_clients_buttons[i].grid(row=row,column=col)
        self.clients_frame.grid(row=2,column=1, sticky='nsew', pady=20, padx=20)
        
        
        
        # блиц режим
        self.blitz_frame = CTkFrame(self)
        self.blitz_label = CTkLabel(self.blitz_frame, text= '1)\n2)\n3)\n4)', font= CTkFont('Comic Sans MS', 72))
        self.blitz_label.grid(row=0,column=0, pady=20, padx=40)
        
        # рамка списка процессов
        self.list_processes_frame = CTkFrame(self)
        self.list_processes_frame.columnconfigure(0, weight=1)
        self.list_processes_frame.rowconfigure((1,2) , weight=1)
        self.list_processes_segbut = CTkSegmentedButton(self.list_processes_frame,
                                                        values= ('Запрещенные',
                                                                 'Разрешенные'),
                                                        command=self.update_list_key_proc)
        self.list_processes_segbut.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky = 'new')
        self.list_processes_textbox = CTkTextbox(self.list_processes_frame, height=self.winfo_screenheight()*0.3)
        self.list_processes_textbox.grid(row=1, column = 0, columnspan=2, padx = 20, sticky = 'nswe')
        # кнопки и поле ввода
        # entry
        self.list_processes_entry = CTkEntry(self.list_processes_frame, placeholder_text='Добавить процесс')
        self.list_processes_entry.grid(row = 2, column = 0, columnspan=2, padx = 20, pady = 20, sticky = 'swe')
        # в хорошую и плохую категорию
        self.list_processes_bott_good = CTkButton(self.list_processes_frame, 
                                                  text='В разрешенную\nкатегорию',
                                                  fg_color= '#32cd32', 
                                                  command=lambda: self.update_DB('gd'))
        self.list_processes_bott_good.grid(row=3, column=0, padx=20, pady=(0,16), sticky = 'n')
        self.list_processes_bott_neut = CTkButton(self.list_processes_frame, 
                                                  text='В запрещенную\nкатегорию',
                                                  fg_color= '#ff5349',  
                                                  command=lambda: self.update_DB('bd'))
        self.list_processes_bott_neut.grid(row=3, column=1, padx=20, pady=(0,16), sticky = 'n')
        # удалить из базы данных
        self.list_processes_bott_bad = CTkButton(self.list_processes_frame, text='Удалить из\nбазы данных',
                                                 fg_color= '#b8860b',  
                                                 command=lambda: self.update_DB('dt'))
        self.list_processes_bott_bad.grid(row=4, column=0, columnspan = 2, padx=20, pady=(0,16), sticky = 'n')

        
        
        # нижняя панель действий
        self.down_panele = CTkFrame(self, height=80, fg_color="transparent")
        self.down_panele.columnconfigure(0,weight=1)
        self.down_panele_but_m = CTkButton(self.down_panele, text='Образовать\nгруппу', 
                                              command=lambda: self.down_but_comm(self.down_panele_but_m))
        self.down_panele_but_m.grid(row=0, column=3, padx=20)
        self.down_panele_but_r = CTkButton(self.down_panele, text='Список ключей-\nпроцессов', 
                                              command=lambda: self.down_but_comm(self.down_panele_but_r))
        self.down_panele_but_r.grid(row=0, column=4)
        self.down_panele.grid(row = 3,column = 1, padx=20, pady=(0,12), sticky = 'nsew')
        
        
        # запустить сервер
        self.close_app = False
        self.start_server()
        
    def down_but_comm(self, but):
        text = but.cget('text').replace('\n',' ')
        if text == 'Список ключей- процессов':
            self.show_list_key_proc()
        elif text == 'Начать блиц':
            self.blitz('start')
        
        elif text == 'Завершить блиц':
            self.blitz('stop')
    
    def blitz(self, comm):
        if comm == 'start': # начать блиц
            if self.server_stage == None: # можно менять
                self.server_stage = 'blz'
                self.draw_message('Блиц начался')
                
                
                
            else:
                self.draw_message('Стадия уже задана')
                    
        elif comm == 'stop':
            if self.server_stage == 'blz': # завершить именно блиц
                self.server_stage = None
                self.draw_message('Блиц завершен')
                
                # обновить очередь
                APP.queue = []
                # Указать изменения в списке
                self.blitz_label.configure(text = '\n'.join(APP.queue))
                
            else:
                self.draw_message('Блиц не был запущен')
                
    def show_list_key_proc(self):
        self.statistic_persenal_frame.grid_forget()
        self.list_processes_frame.grid(row = 1, column = 0, rowspan = 3, padx = (0,0), sticky = 'nsew')
        self.list_processes_segbut.set('Запрещенные')
        self.update_list_key_proc()
    
    def update_list_key_proc(self, value = 'Запрещенные'):
        if value == 'Запрещенные':
            prc = self.bad_pr
            color = '#ff5349'
        else:
            prc = self.good_pr
            color ='#32cd32'
        
        self.list_processes_segbut.configure(selected_color = color)   
        self.list_processes_textbox.delete('0.0','end')
        self.list_processes_textbox.insert('0.0','\n'.join(prc))
        
    def draw_message(self, mes='Приветсвую/Первый вход'):
        def start_draw():
            i = 0
            
            self.terminal_label.configure(text = self.queue_mes[-1])
            # создать эффект мерцания
            while i<5:
                
                # серый
                self.terminal_label.configure(text_color = '#808080')
                sleep(0.05)
                # черный
                self.terminal_label.configure(text_color = '#000000')
                sleep(0.1)
                
                i += 1
                
                if len(self.queue_mes) != 1: # Новое сообщение
                    i = 0
                    self.queue_mes.pop(0) # удаляю предыдущее
              
            self.queue_mes.pop(0)
                    
        # меняю / на \n и добавляю в список
        self.queue_mes.append(mes.replace('/','\n'))
        if len(self.queue_mes) == 1: # новое сообщение, запускаю цикл
            g = Thread(target=start_draw)
            g.start()
    
    def start_server(self):
        date_s = datetime.datetime.today().__str__()

        # прочитать порт
        with open('PORT.txt') as P:
            PORT = int(P.readline())
            del(P)
        
        # каково задание сервера
        self.server_stage = None
        def connect(conn):
            def send(string):
                conn.send(string.encode())
            def recive():
                return (conn.recv(1024)).decode()
            
            with conn:
                # получить date и id
                data = recive()
                conn_date, conn_id = data.split('/')
                conn_id = int(conn_id)
                
                # время старта сходится, а id есть в списке
                if conn_date == date_s:
                    
                    send('pass')

                    # вернулся ли пользователь обратно
                    data = recive()
                    if data == '/bck': # он только вернулся
                        # вывести в табло
                        self.draw_message(f'{self.dict_clients[conn_id]} вернулся!')
                        # отображаю
                        self.dict_clients_buttons[conn_id].configure(text = self.dict_clients[conn_id],fg_color = '#edff21' ,text_color = '#4c4f4c')
                        return()
                    else:
                        send('//ok')
                        

                    # сортировка
                    # region
                    # получаю отчет
                    data = loads(conn.recv(1024))
                    
                    # сортировка
                    info_pr = [[],[],[]]
                    sorted_len_pr = [0,0,0]
                    for pr in data:
                        pr_low = pr.lower()
                        # определить, является ли этот процесс нежелательным
                        if any(key_w in pr_low for key_w in self.bad_pr):
                            ind = 2
                        elif any(key_w in pr_low for key_w in self.good_pr): # разрешенный
                            ind =0
                        else: # нейтральные
                            ind = 1
                        
                        
                        sorted_len_pr[ind] += 1
                        # нужно ли отображать инфу
                        info_pr[ind].append(pr)
                            
                            
                        # проверить, новый ли это процесс
                        self.check_pr(pr)
                    self.dict_cntr[conn_id] = (tuple(sorted_len_pr), int(time()))
                    
                    # обновить данные фокуса
                    if conn_id == APP.focus_pers:
                        self.show_info_pers(info_pr)
                    
                    # сохранить данные
                    self.save_processes(info_pr, conn_id)

                    
                    # диаграммы отчета 
                    all_prs = [0,0,0]
                    for i in tuple(self.dict_cntr.values()):
                        if i != ():
                            for j in range(3):
                                all_prs[j] += i[0][j]
                    
                    # диаграммы и кнопка
                    self.data_diag = tuple(all_prs)
                    self.data_id = conn_id
                    self.after(10, self.update_diag)
                    #endregion 


                    # комманды!
                    send('next')
                    # действия клиента
                    # region
                    data = recive()
                    if data != '0':
                        try:
                            comm = data
                        
                            if comm == 'cls' and date_s == conn_date: # клиент закрыл приложение
                                self.draw_message(f'{APP.dict_clients[conn_id]} покинул сервер!')
                                self.dict_clients_buttons[conn_id].configure(fg_color='#cccccc')
                            
                            elif 'blz' in comm and self.server_stage == 'blz': 
                                
                                if comm == 'blz_in': # встать в очередь
                                    # Если персонажа нет в списке, то добавить
                                    if conn_id not in APP.queue:
                                        print('add')
                                        APP.queue.append(conn_id)
                                else: # покинуть
                                    # Если персонажа есть в списке, то удалить
                                    if conn_id in APP.queue:
                                        APP.queue.pop(APP.queue.index(conn_id))
                                    
                                queue = [f'{i+1}) {self.dict_clients[id]}' for i,id in enumerate(APP.queue[:4])]  
                                # Указать изменения в списке
                                self.blitz_label.configure(text = '\n'.join(queue))
                
                        except Exception as er:
                            self.draw_message('Ошибка в уведомлении')
                            print(str(er))
                    # endregion
                    
                    
                    # отправить текущую стадию клиенту
                    #region
                    if self.server_stage == None:
                        conn.send('0'.encode())
                        
                    elif self.server_stage == 'blz':
                        id = 0 if conn_id not in APP.queue else APP.queue.index(conn_id) + 1
                        send(f'blz/{id}')
                    else:
                        conn.send(self.server_stage.encode())
                    # endregion
                        
                    
                else: # надо регистрироваться
                    send('rgst')
                    
                    unswer = recive()
                    if unswer != '//ok': # клиент хочет зарегестрироваться
                        # проверяю существование идентичных имен
                        names = [name.upper() for name in APP.dict_clients.values()] # список имен с верхнего регистра. Был замечен баг.
                        if unswer.upper() not in names: # нет
                            # генерирую id
                            id = len(APP.dict_clients)
                            send(f'{id}/{date_s}')
                            
                            # вывести в табло
                            self.draw_message(f'{unswer} присоединился!')
                            
                            # добавить в словарь процессов
                            self.dict_cntr[id] = ((0,0,0), int(time()))
                                
                            # добавляю имя
                            APP.dict_clients[id] = unswer   

                            # отображаю
                            self.dict_clients_buttons[id].configure(text = unswer,fg_color = '#edff21' ,text_color = '#4c4f4c')
                            
                            
                        else:
                            conn.send('//has'.encode())
                    
                    else: # проверка версий
                        send(serv_version)
        
        def start():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                server.bind(('0.0.0.0', PORT)) #Принимать все
                server.listen(16)
                
                server.settimeout(5)
                # запускаю цикл на ожидание неоднократных подключений
                self.close_app = False
                last_time = datetime.datetime.now()
                while APP.run_server:
                    
                    
                    # ожидать окончания сервера
                    try:
                        conn, addr = server.accept()
                        
                    except TimeoutError:
                        # проверка последнего подключения
                        if (datetime.datetime.now() - last_time).total_seconds() > 30: # давно нет подключений
                            self.draw_message('Нет подключений!')
                        pass
                    else:
                        try: # отследить разрыв
                            connect(conn)
                        except Exception as ex:
                            self.draw_message('Разорвано подключение!')  
                            print(ex)
                            
                        # потеряшки
                        try:
                            if (datetime.datetime.now() - last_time).total_seconds() > 20: # проверять каждые 20 секунд
                                last_time = datetime.datetime.now()
                                for i in tuple(APP.dict_clients.keys()):
                                    if self.dict_clients_buttons[i].cget('fg_color') not in ('#cccccc','#dcdcdc'):
                                        # проверяю последнее вхождение
                                        if int(time()) - self.dict_cntr[i][1]>15: # прошло больше 15 сек с последнего отчета
                                            self.draw_message(f'{APP.dict_clients[i]} пропал без вести!')
                                            self.dict_clients_buttons[i].configure(fg_color = '#cccccc')
                        except Exception as er:
                            self.draw_message('Ошибка в поиске потеряшек')
                            print(er)  
                            
            self.close_app = True

        server = Thread(target=start)
        server.start()
        
        self.draw_message('Сервер запущен')

    def change_frame(self, frame):
        frames = (self.clients_frame, self.blitz_frame)
        for f in frames:
            f.grid_forget()
        
        frame.grid(row=2,column=1, sticky='nsew', pady=20, padx=20)
        
    def menu_action(self, value):
        # отключить сервер
        if value == 'Отключить подключения':
            self.draw_message('Идет отключение...')
            self.server_stage = 'cls'
            
        elif value == 'Блиц режим':
            self.change_frame(self.blitz_frame)
            
            # сменить кнопки
            self.down_panele_but_r.configure(text = 'Начать\nблиц')
            self.down_panele_but_m.configure(text = 'Завершить\nблиц')
        
        elif value == 'Главный экран':
            self.change_frame(self.clients_frame)
            
            # сменить кнопки
            self.down_panele_but_r.configure(text = 'Образовать\nгруппу')
            self.down_panele_but_m.configure(text = 'Список ключей-\nпроцессов')
    
    def update_DB(self, type_act):
        
        data = self.list_processes_entry.get()
        if data != '':
            data = data.lower()
            
            # поиск такого процесса
            self.cursor.execute('SELECT * FROM KW WHERE key_word LIKE (?)', (data,))
            proc = self.cursor.fetchone()
            
            # если разрешенная категория
            if type_act in ('gd','bd'):
                if proc == None:
                    self.cursor.execute('INSERT INTO KW (key_word, type) VALUES (?, ?)', (data, type_act))
                    self.connection.commit()
                    
                    # база данных
                    # хорошие и плохие процессы
                    self.cursor.execute('SELECT key_word FROM KW WHERE type LIKE "bd"',)
                    APP.bad_pr = tuple([i[0] for i in self.cursor.fetchall()])
                    self.cursor.execute('SELECT key_word FROM KW WHERE type LIKE "gd"',)
                    APP.good_pr = tuple([i[0] for i in self.cursor.fetchall()])
                    
                    self.draw_message('Ключ-процесс добавлен')
                    # очистить и снять фокус
                    self.list_processes_entry.delete(0, END)
                    self.focus()
                
                else:
                    self.draw_message('Такой ключ-процесс уже есть')
            
            else:
                if proc != None: # такой процесс должен существовать
                    self.cursor.execute('DELETE FROM KW WHERE key_word = ?', (data,))
                    
                    # база данных
                    # хорошие и плохие процессы
                    self.cursor.execute('SELECT key_word FROM KW WHERE type LIKE "bd"',)
                    APP.bad_pr = tuple([i[0] for i in self.cursor.fetchall()])
                    self.cursor.execute('SELECT key_word FROM KW WHERE type LIKE "gd"',)
                    APP.good_pr = tuple([i[0] for i in self.cursor.fetchall()])
                    
                    self.draw_message('Ключ-процесс удален')
                    # очистить и снять фокус
                    self.list_processes_entry.delete(0, END)
                    self.focus()
                    
                else:
                    self.draw_message('Нет такого ключа-процесса')
        
        else:
            self.draw_message('Вы не ввели процесс')
        
    def update_diag(self): # диаграммы
        prs = list(self.dict_cntr[self.data_id][0])
        prs.reverse()
        ind = prs.index(max(prs))
        if prs[0] != 0: # красный
            color = '#ff4e33'
        elif ind ==1: #желтый
            color = '#edff21'
        else: #зеленый
            color ='#32cd32'
        
        # поменять цвет
        if self.dict_clients_buttons[self.data_id].cget('fg_color') != '#cccccc':
            self.dict_clients_buttons[self.data_id].configure(fg_color = color)
        
        # диаграммы
        diag_s = (self.statistic_all_diag_g, self.statistic_all_diag_y, self.statistic_all_diag_r)
        for i in range(3):
            persent = self.data_diag[i]/sum(self.data_diag)
            h = int(150 * persent)
            diag_s[i].configure(height = h, text = f'{int(persent*100)}%')

    def save_processes(self, data, id):
        def save():
            # подчищаю
            self.cursor.execute('DELETE FROM PS WHERE id = (?)',(id,))
            # добавляю новое
            type_proc = ['gd','nd','bd']
            for i, type_p in enumerate(data):
                for pr in type_p:
                    pr = pr.lower()
                    self.cursor.execute('INSERT INTO PS (id, process, type_p) VALUES (?, ?, ?)', (id, pr, type_proc[i]))

        self.after(10,save)

    def show_info_pers(self, info_prs = None):
        
        def update(info_prs = info_prs):
            
            name = self.dict_clients_buttons[APP.focus_pers].cget('text')
            
            # время
            if info_prs == None: # архив
                time_c = int(time() - self.dict_cntr[APP.focus_pers][1])
                time_c = f'{time_c//60}:{time_c%60}'
                print(time_c)
            # архивные ли процессы
            text = f'{name}\n\nПроцессы:' if info_prs != None else f'{name}\n\nАрхив({time_c}):'
            self.statistic_persenal_title.configure(text = text)
            
            # подгрузить старые процессы, если info_prs пустой
            
            if info_prs == None:
                # достать плохие, нейтральные, а затем разрешеннные процессы
                type_p = ['gd','nd','bd']
                info_prs = []
                for j in range(3):
                    self.cursor.execute('SELECT process FROM PS WHERE id = (?) AND type_p = (?)', (self.focus_pers,type_p[j]))
                    k = [i[0] for i in self.cursor.fetchall()]
                    info_prs.append(k)
            
            
            # редактировать процессы
            i_t = 1
            new_prs = [[],[],[]]
            for ind_i,type_i in enumerate(tuple(reversed(info_prs))): # пробегаю по типам процессов
                for pr in type_i: # пробегаю по процессам
                    pr = f'{i_t}) {pr}'

                    upg_pr = []
                    i = 0
                    while 1:
                        # проверяю первый символ - 
                        while pr[i] == ' ':
                            i+=1
                        upg_pr.append(pr[i:i+30])
                        i += 30
                        
                        if i >= len(pr):
                            break

                    new_prs[ind_i].append('\n'.join(upg_pr))
                    i_t += 1
            
            # изменить список
            labels = (self.statistic_persenal_list_r,self.statistic_persenal_list_y,self.statistic_persenal_list_g)
            for i in range(3):
                if new_prs[i] != []:
                    text_l = '\n\n'.join(new_prs[i])
                    labels[i].configure(text = text_l)
                else:
                    labels[i].configure(text = '')

        if self.dict_clients_buttons[APP.focus_pers].cget('fg_color') != '#dcdcdc':
            self.after(10, update)

    def change_focus(self, id):
        # Отобразить панель клиента
        self.list_processes_frame.grid_forget()
        self.statistic_persenal_frame.grid(row = 1, column = 0, rowspan = 3, padx = (0,0), sticky = 'nsew')
        
        APP.focus_pers = id
        
        self.show_info_pers()
    
    def change_name(self):
        if APP.focus_pers != None and self.dict_clients_buttons[APP.focus_pers].cget('fg_color') != '#dcdcdc':
            if self.statistic_persenal_ch_name_entry.winfo_ismapped(): # активна ли кнопка
                self.statistic_persenal_ch_name_entry.grid_forget()
                self.statistic_persenal_change_name.configure(text = 'Изменить\nимя')
                
                # проверка имени
                data = self.statistic_persenal_ch_name_entry.get()
                if data != '': #пользователь ввел имя
                    # имя не должно содержать некоторые знаки
                    if '*' not in data and '/' not in data:
                        # имя не должно содержать больше 13 символов
                        if len(data)<= 13:
                            self.dict_clients[APP.focus_pers] = data

                            self.dict_clients_buttons[APP.focus_pers].configure(text = data)
                            
                        else:
                            self.draw_message('Используйте меньше 13 знаков')
                        
                        
                    else:
                        self.draw_message('Есть запрещенные знаки!')
                        self.statistic_persenal_change_name.delete(0, END)
                    
                    
                else:
                    self.draw_message('Введите имя!')
            else:
                self.statistic_persenal_ch_name_entry.grid(row=2, column = 0,pady = (0,6), sticky = 's')
                self.statistic_persenal_ch_name_entry.delete(0, END)
                self.focus()
                self.statistic_persenal_change_name.configure(text = 'Изменить')
        else:
            self.draw_message('Выберите клиента') 

    
    def check_pr(self, pr):
        def check():
            # self.cursor.execute('SELECT * FROM PS')
            # print(self.cursor.fetchall())
            self.cursor.execute('SELECT * FROM PS WHERE process = (?)',(pr.lower(),))
            if self.cursor.fetchone() == None:
                self.statistic_all_list.insert("0.0", f'{pr}\n\n')
            # self.statistic_all_list.insert("1.0", f'{pr}\n\n')
        
        self.after(10, check)
    
    def clean_list_prs(self):
        self.statistic_all_list.delete('0.0','end')
   
    def show_worst_cl(self):
        if self.dict_cntr != {}:
            vals = self.dict_cntr.values()
            vals = [i[0] for i in vals]
            maxval = max([i[2] for i in vals])
            
            # поиск списка
            for i in vals:
                if i[2] == maxval:
                    maxval = i
                    break
                    
            # поиск ключа по списку
            for key_i, val_i in self.dict_cntr.items():
                if val_i[0] == maxval:
                    key_i
                    break
            
            APP.focus_pers = key_i
            self.show_info_pers()
        
app = APP()

def on_closing():
    # app.draw_message('Идет выключение сервера...')
    APP.run_server = False
    # ожидать закрытие сервера
    while app.close_app and active_count() > 2:
        pass
    app.destroy()
    print('Сервер выключен')

app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()

# выключить БД
app.connection.commit()
app.connection.close()