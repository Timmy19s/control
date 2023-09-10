#Import the required Libraries
from tkinter import *

#Create an instance of tkinter frame
win = Tk()

#Set the geometry of tkinter frame
win.geometry("750x250")

#Create a Text Box
text= Text(win, width= 50, height= 30, background=
"gray71",foreground="#fff",font= ('Sans Serif', 13, 'italic bold'))

#Insert the text at the begining
text.insert(INSERT, "Write Something About Yourself\n\n")
text.pack(expand= 1, fill= BOTH)

text.insert('0.0', "Игддырше\n\n")

text.insert('1.0', "hhfff\n\n")

win.mainloop()