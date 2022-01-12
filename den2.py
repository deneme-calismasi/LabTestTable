import tkinter as tk  # PEP8: `import *` is not preferred
from tkinter import ttk
import csv


# --- functions ----

def load_csv():
    with open("new.csv") as myfile:
        csvread = csv.reader(myfile, delimiter=',')

        for row in csvread:
            print('load row:', row)
            tree.insert("", 'end', values=row)


def save_csv():
    with open("new.csv", "w", newline='') as myfile:
        csvwriter = csv.writer(myfile, delimiter=',')

        for row_id in tree.get_children():
            row = tree.item(row_id)['values']
            print('save row:', row)
            csvwriter.writerow(row)


# --- main ---

root = tk.Tk()

tree = ttk.Treeview(root, height=25, selectmode='extended')
tree.pack()

tree["columns"] = ("one", "two", "three", "four")
tree.column("one", width=120)
tree.column("two", width=160)
tree.column("three", width=130)
tree.column("four", width=160)
tree.heading("one", text="Numer seryjny leku")
tree.heading("two", text="Nazwa Leku")
tree.heading("three", text="Ilość ampułek")
tree.heading("four", text="Data ważności")
tree["show"] = "headings"

button_load = tk.Button(root, text='Load', command=load_csv)
button_load.pack()
button_save = tk.Button(root, text='Save', command=save_csv)
button_save.pack()

# add some data for test
tree.insert("", 'end', values=[1, "A", "B", "C"])
tree.insert("", 'end', values=[2, "X", "Y", "Z"])

root.mainloop()
