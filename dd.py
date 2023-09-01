from customtkinter import (CTk,
                           CTkFrame,
                           CTkProgressBar,
                           CTkLabel,
                           CTkButton,
                           CTkEntry,
                           CTkFont)

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
        
        
        # шрифт
        self.font = CTkFont('Comic Sans MS', 20, 'bold')
        
        # создать словарь разметок
        self.dict_frames = {}
            
        # терминал
        self.terminal_frame = Frames(self,'terminal' ,0, 0, 220)
        # self.terminal_frame.grid_propagate(False) # запретить изменять размер
        self.terminal_label = CTkLabel(self.terminal_frame, text='Info', font= CTkFont('Comic Sans MS', 24), justify = 'left')
        self.terminal_label.grid(row=0,column=0,pady=(0,20),padx=10, sticky = 'ew')
        self.load_bar = CTkProgressBar(self.terminal_frame)
        self.load_bar.grid(row=1,column=0,pady=(0,20),padx=10)
        
        self.terminal_frame.grid(row=0, column=0, pady = 20, padx=30, sticky='we')
        
        
        # регистрация
        self.regist_frame = Frames(self, 'regist', (0,1),0)
        self.regist_button_add = CTkButton(self.regist_frame, text = 'отправить', font = self.font)
        self.regist_button_add.grid(row=1,column=1,pady=10,padx=20, sticky = 'se')
        self.regist_button_next = CTkButton(self.regist_frame, text = 'дальше', font = self.font)
        self.regist_button_next.grid(row=1,column=0,pady=10,padx=20, sticky = 'se')
        self.regist_entry = CTkEntry(self.regist_frame, placeholder_text='Введите ваше имя', font = self.font)
        self.regist_entry.grid(row=0,column=0,pady=10,padx=20, columnspan=2, sticky = 'we')
        
        # self.regist_frame.grid(row=1, column=0, pady = (0,20), padx=20, sticky='we')
        
        self.no_conn_frame = Frames(self,'no_conn', 0, (0,1))
        self.no_conn_button = CTkButton(self.no_conn_frame, text = 'поменять', font = self.font)
        self.no_conn_button.grid(row=0,column=1,pady=10,padx=20, sticky = 'se')
        self.no_conn_entry = CTkEntry(self.no_conn_frame, placeholder_text='Код', font = self.font, width=60)
        self.no_conn_entry.grid(row=0,column=0,pady=10,padx=20, sticky = 's')
        
        self.no_conn_frame.grid(row=1, column=0, pady = (0,20), padx=20, sticky='we')
        
        
        self.bar_f = True
        
    def switch_bar(self):
        if self.bar_f == True:
            self.load_bar.set(0.5)
            self.load_bar.configure(mode='indeterminate')
            self.load_bar.start()
            self.bar_f = False
        
        else:
            self.load_bar.set(1)
            self.load_bar.configure(mode='determinate')
            self.load_bar.stop()
            self.bar_f = True
        

app = APP()
app.mainloop()