import socket
from threading import Thread
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
                           CTkTextbox)
from PIL import Image
from pickle import loads
import sqlite3


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
    
    def __init__(self):
        super().__init__()
        
        # окно
        self.title("server")
        self.geometry(f"{int(self.winfo_screenwidth()*0.9)}x{int(self.winfo_screenheight()*0.5)}+0+0")
        
        
        
        # позволить растягиваться
        self.grid_columnconfigure(1,weight=8)
        self.grid_columnconfigure((0,2),weight=1)
        self.grid_rowconfigure(2,weight=1)
        
        
        
        # панель задач
        self.menu_tab = CTkSegmentedButton(self, height=40, values= ('Главное меню',
                                                          'Блиц режим',
                                                          'Голосование',
                                                          'Обмен файлами',
                                                          'Выключить сервер'),
                                           command=self.menu_action)
        self.menu_tab.set('Главное меню')
        self.menu_tab.grid(row=0,column=0, columnspan = 2, sticky = 'nwe')
        
        
        
        # терминал
        self.queue_mes = []
        self.text_for_term = '' # текст для терминала
        
        self.terminal_frame = CTkFrame(self, height=80)
        self.terminal_label = CTkLabel(self.terminal_frame, text='Info', font= CTkFont('Comic Sans MS', 32), justify = 'left')
        self.terminal_label.grid(row=0,column=0,pady=20,padx=30)
        
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
        self.statistic_all_button.grid(row=3, column = 0, sticky = 's')
        
        
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
        self.statistic_persenal_button = CTkButton(self.statistic_persenal_frame, text = 'Показать\nплохиша', command=self.show_worst_cl)
        self.statistic_persenal_button.grid(row=2, column = 0, sticky = 's')
        
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
        self.clients_frame.grid(row=2,column=1, sticky='nsew')    
        
        
        
        # добавить процесс в список
        self.add_process_frame = CTkFrame(self, height=80, fg_color="transparent")
        self.add_process_frame.columnconfigure(0,weight=1)
        self.add_process_entry = CTkEntry(self.add_process_frame, placeholder_text='Добавить процесс')
        self.add_process_entry.grid(row = 0, column = 0, sticky = 'we')
        self.add_process_bott_good = CTkButton(self.add_process_frame, 
                                               text='В разрешенную\nкатегорию', 
                                               command=lambda: self.update_DB('gd'))
        self.add_process_bott_good.grid(row=0, column=1)
        self.add_process_bott_neut = CTkButton(self.add_process_frame, 
                                               text='В запрещенную\nкатегорию', 
                                            command=lambda: self.update_DB('bd'))
        self.add_process_bott_neut.grid(row=0, column=2)
        self.add_process_bott_bad = CTkButton(self.add_process_frame, text='Удалить из\nбазы данных', 
                                              command=lambda: self.update_DB('dt'))
        self.add_process_bott_bad.grid(row=0, column=3)
        self.add_process_frame.grid(row = 3,column = 1, sticky = 'nsew')
        
        
        
        
        # запустить сервер
        self.close_app = False
        self.start_server()
    
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
    
    def start_server(self):
        date = datetime.datetime.today().__str__()

        # прочитать порт
        with open('PORT.txt') as P:
            PORT = int(P.readline())
            del(P)

        dict_clients = {}

        def start():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                server.bind(('0.0.0.0', PORT)) #Принимать все
                server.listen(16)
                
                server.settimeout(5)
                # запускаю цикл на ожидание неоднократных подключений
                self.close_app = False
                while APP.run_server:
                    

                    # ожидать окончания сервера
                    try:
                        conn, addr = server.accept()
                    except TimeoutError:
                        pass
                    else:
                        with conn:
                            try:
                                data = (conn.recv(1024)).decode()
                            except UnicodeDecodeError:
                                self.draw_message('проблемма с юникодом')
                            else:
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
                                            
                                            self.draw_message(f'{name} присоединился!')
                                            
                                            # добавить в словарь процессов
                                            self.dict_cntr[id] = ((0,0,0), int(time()))
                                            
                                        else:
                                            conn.send(f'//rename'.encode())
                                            id = int(id)
                                            
                                            self.draw_message(f'{name} вернулся!')
                                            
                                        # добавляю или меняю
                                        dict_clients[id] = name    
                                        
                                        
                                        # отображаю
                                        self.dict_clients_buttons[id].configure(text = name,fg_color = '#edff21' ,text_color = '#4c4f4c')
                                        
                                            
                                    else:
                                        conn.send('//has'.encode())

                                elif comm == 'ctrl': # клиент отправляет отчет
                                    id = int(data)
                                    
                                    # получить отчет
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
                                    
                                    if id == APP.focus_pers:
                                        self.show_info_pers(info_pr)
                                    
                                    # сохранить данные
                                    self.save_processes(info_pr, id)
                                    # сверить время и изменить dict_ctrl
                                    # if id in self.dict_cntr:
                                    #     print('ds')
                                        # if self.dict_cntr[id][1] - int(time()) > 30: # не отвечает
                                        #     self.dict_clients_buttons[id].configure(fg_color='#cccccc')
                                    # if id == 1:
                                    #     print()
                                    self.dict_cntr[id] = (tuple(sorted_len_pr), int(time()))
                                    
                                    

                                    # суммирую 
                                    all_prs = [0,0,0]
                                    for i in tuple(self.dict_cntr.values()):
                                        if i != ():
                                            for j in range(3):
                                                all_prs[j] += i[0][j]
                                    
                                    # диаграммы и кнопка
                                    self.data_diag = tuple(all_prs)
                                    self.data_id = (id)
                                    self.after(10, self.update_diag)
                                    
                                
            
                                elif comm == 'cls': # клиент уведомляет о выключении проги
                                    self.dict_clients_buttons[int(data)].configure(fg_color='#cccccc')
                                    
            self.close_app = True

        server = Thread(target=start)
        server.start()
        
        self.draw_message('Сервер запущен')

    def menu_action(self, value):
        # отключить сервер
        if value == 'Выключить сервер':
            self.draw_message('Идет выключение сервера...')
            APP.run_server = False
    
    def update_DB(self, type_act):
        
        data = self.add_process_entry.get()
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
                    
                    self.draw_message('Этот ключ-процесс теперь нейтрален')
                    
                else:
                    self.draw_message('Нет такого ключа-процесса')
        
        else:
            self.draw_message('Вы не ввели процесс')
        
    def update_diag(self): # диаграммы
        prs = list(self.dict_cntr[self.data_id][0])
        prs.reverse()
        ind = prs.index(max(prs))
        if ind == 0: # красный
            color = '#ff0033'
        elif ind ==1: #желтый
            color = '#edff21'
        else: #зеленый
            color ='#32cd32'
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
        def update():
            nonlocal info_prs
            name = self.dict_clients_buttons[APP.focus_pers].cget('text')
            
            # архивные ли процессы
            text = f'{name}\n\nПроцессы:' if info_prs != None else f'{name}\n\nАрхив:'
            self.statistic_persenal_title.configure(text = text)
            
            # подгрузить старые процессы, если info_prs пустой
            
            if info_prs == None:
                self.cursor.execute('SELECT process FROM PS WHERE id = (?)', (self.focus_pers,))
                info_prs = [[],[i[0] for i in self.cursor.fetchall()],[]]
            
            
            # редактировать процессы
            i_t = 1
            for ind_i,type_i in enumerate(info_prs):
                for ind_pr, pr in enumerate(type_i):
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

                    info_prs[ind_i][ind_pr] = '\n'.join(upg_pr)
                    i_t += 1
            
            # изменить список
            info_prs = list(reversed(info_prs))
            labels = (self.statistic_persenal_list_r,self.statistic_persenal_list_y,self.statistic_persenal_list_g)
            for i in range(3):
                if info_prs[i] != []:
                    text_l = '\n\n'.join(info_prs[i])
                    labels[i].configure(text = text_l)

        self.after(10, update)

    def change_focus(self, id):
        APP.focus_pers = id
        
        self.show_info_pers()
        
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
    while app.close_app:
        pass
    app.destroy()
    print('Сервер выключен')

app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()

# выключить БД
app.connection.commit()
app.connection.close()