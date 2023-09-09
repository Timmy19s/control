from tkinter import *
app = Tk()


def which_button(button_press):
   print (button_press)
   
b1 = Button(app, text="#Text you want to show in button b1",
            command=lambda m="#Text you want to show when\
            b1 is clicked": which_button(m))
            
b1.grid(padx=10, pady=10)

b2 = Button(app, text="#Text you want to show in button b2",
            command=lambda m="#Text you want to show when \
            b2 is clicked": which_button(m))
            
b2.grid(padx=10, pady=10)


app.mainloop()