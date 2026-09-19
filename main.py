from tkinter import *

root = Tk()
root.title("2Do")

myLabel = Label(root, text="Yo this is the label")
myLabel2 = Label(root, text="grid1") #possible to .grid here since its OR lang
myLabel3 = Label(root, text="grid2")

def click1():
    Label1 = Label(root, text="new task created")
    Label1.grid(row=1, column=1)

myButton = Button(root, text="Click it", padx=10, pady=5, command=click1, fg="Red")

myLabel.grid(row=0, column=0)
myLabel2.grid(row=2, column=2)
myLabel3.grid(row=3, column=3)
myButton.grid(row=0, column=1)

root.mainloop()