import math
from pyModbusTCP.client import ModbusClient
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import *
import pymongo
import datetime as dt
import csv

root = tk.Tk()


def window_unit():
    root.title("Sensor's Temperatures °C")
    root.geometry("800x600")
    root.grid()


class ModBus:
    sensor_min_num = 0
    sensor_max_num = 2
    lineNo = 0
    sensorTypeNo = 0

    def __init__(self, sensorTypeNo, lineNo, sensor_min_num, sensor_max_num):

        self.sensor_min_num = sensor_min_num
        self.sensor_max_num = sensor_max_num
        self.lineNo = lineNo
        self.sensorTypeNo = sensorTypeNo
        self.resultList = []
        self.regNoList = []
        self.reg_list = list(range(self.sensor_min_num, self.sensor_max_num + 1))
        self.style = ttk.Style()
        self.style.map("Treeview", foreground=self.fixed_map("foreground"), background=self.fixed_map("background"))

    def fixed_map(self, option):
        return [elm for elm in self.style.map("Treeview", query_opt=option) if elm[:2] != ("!disabled", "!selected")]

    def connect_modbus(self):
        print("---------------------------------------")
        for i in self.reg_list:
            groupNo = math.floor(((self.lineNo - 1) / 256)) + 1
            self.portNo = 10000 + (self.sensorTypeNo - 1) * 10 + groupNo - 1
            regNo = (((self.lineNo - 1) * 128 + (int(i) - 1)) * 2) % 65536
            self.regNoList.append(regNo)
            print("groupNo", groupNo)
            print("portNo", self.portNo)
            print("regNo", regNo)

        for x in self.regNoList:
            sensor_no = ModbusClient(host="192.40.50.107", port=self.portNo, unit_id=1, auto_open=True)
            sensor_no.open()
            regs = sensor_no.read_holding_registers(x, 2)
            if regs:
                print(regs)
            else:
                print("read error")

            regs[0], regs[1] = regs[1], regs[0]
            data_bytes = np.array(regs, dtype=np.uint16)
            result = data_bytes.view(dtype=np.float32)
            self.resultList.append(result[0])

        print("REG_LIST", self.reg_list)
        self.data_as_float = self.resultList
        print("Result_Temp", self.resultList)
        print("??????????????????????????????????????????????")
        self.regNoList = []
        self.resultList = []
        return self.data_as_float

    def list_to_dict(self):
        self.connect_modbus()
        self.regs_count = len(self.reg_list)

        value = [[num for num in range(1, 1 + self.regs_count)], self.reg_list, self.data_as_float]

        data = np.array(value).T.tolist()

        products = data
        self.arr = []
        for product in products:
            vals = {}
            vals["Sensor Type No"] = str(int(self.sensorTypeNo))
            vals["Line No"] = str(int(self.lineNo))
            vals["Sensor No"] = str(int(product[1]))
            vals["Temp"] = str(round(product[2], 4))
            vals["Time"] = str(dt.datetime.now().strftime('%Y-%m-%d %X'))
            self.arr.append(vals)
        return self.arr

    def record_mongo(self):
        lst = self.list_to_dict()
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["Modbus_Database"]
        mycol = mydb["collection5"]

        mycol.insert_many(lst)

        documents = list(mycol.find({}, {'_id': 0}))
        res = [list(idx.values()) for idx in documents]

        for index1, row in enumerate(res):
            for index2, item in enumerate(row):
                try:
                    res[index1][index2] = (float(item))
                except ValueError:
                    pass
        return res

    def load_csv(self):
        with open("new.csv") as myfile:
            csvread = csv.reader(myfile, delimiter=',')

            for row in csvread:
                print('load row:', row)
                self.tree.insert("", 'end', values=row)

    def save_csv(self):
        with open("new.csv", "w", newline='') as myfile:
            csvwriter = csv.writer(myfile, delimiter=',')

            for row_id in self.tree.get_children():
                row = self.tree.item(row_id)['values']
                print('save row:', row)
                csvwriter.writerow(row)

    def drag_start(self, event):
        widget = event.widget
        widget.startX = event.x
        widget.startY = event.y

    def drag_motion(self, event):
        widget = event.widget
        x = widget.winfo_x() - widget.startX + event.x
        y = widget.winfo_y() - widget.startY + event.y
        widget.place(x=x, y=y)

    def table_insert(self, x, y):

        if self.sensorTypeNo == 1:
            self.head_text = "L1"
        elif self.sensorTypeNo == 2:
            self.head_text = "L2"
        elif self.sensorTypeNo == 3:
            self.head_text = "L3"
        elif self.sensorTypeNo == 7:
            self.head_text = "OUT"
        elif self.sensorTypeNo == 8:
            self.head_text = "EXT"
        else:
            self.head_text = "NULL"

        self.tree = ttk.Treeview(root)
        verscrlbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)

        self.tree.configure(xscrollcommand=verscrlbar.set)

        self.tree["columns"] = ("1", "2", "3", "4")

        self.tree['show'] = 'headings'

        self.tree.column("1", width=65, minwidth=30, anchor='c')
        self.tree.column("2", width=125, minwidth=30, anchor='c')
        self.tree.column("3", width=65, minwidth=30, anchor='c')
        self.tree.column("4", width=115, minwidth=30, anchor='c')

        self.tree.heading("1", text=self.head_text)
        self.tree.heading("2", text="Time")
        self.tree.heading("3", text="Sensor No")
        self.tree.heading("4", text="Temperature °C")

        self.tree.place(x=x, y=y)

        self.tree.tag_configure('high', foreground='red')
        self.tree.tag_configure('low', foreground='black')

        self.button_load = tk.Button(root, text='Load', command=self.load_csv)
        self.button_load.place(x=x, y=y + 230)
        self.button_save = tk.Button(root, text='Save', command=self.save_csv)
        self.button_save.place(x=x, y=y + 260)

        self.button_load.bind("<Button-1>", self.drag_start)
        self.button_save.bind("<B1-Motion>", self.drag_motion)

        start_range = 0
        id_count = 1

        for record in self.record_mongo()[-(self.regs_count):]:
            sensor_id = record[2]
            temperature = record[3]
            date_time = record[4]
            if float(temperature) > 30.0:
                self.tree.insert("", index='end', text="%s" % int(sensor_id), iid=start_range,
                                 values=(str(self.head_text), str(date_time), int(sensor_id), float(temperature)),
                                 tags=('high',))
            else:
                self.tree.insert("", index='end', text="%s" % int(sensor_id), iid=start_range,
                                 values=(str(self.head_text), str(date_time), int(sensor_id), float(temperature)),
                                 tags=('low',))

            start_range += 1
            id_count += 1

        self.tree.bind("<Button-1>", self.drag_start)
        self.tree.bind("<B1-Motion>", self.drag_motion)

        self.update_window_table()
        self.tree.after(20000, self.update_window_table)

    def update_window_table(self):

        for i in self.tree.get_children():
            self.tree.delete(i)

        start_range = 0
        id_count = 1

        for record in self.record_mongo()[-(self.regs_count):]:
            sensor_id = record[2]
            temperature = record[3]
            date_time = record[4]
            if float(temperature) > 30.0:
                self.tree.insert("", index='end', text="%s" % int(sensor_id), iid=start_range,
                                 values=(str(self.head_text), str(date_time), int(sensor_id), float(temperature)),
                                 tags=('high',))
            else:
                self.tree.insert("", index='end', text="%s" % int(sensor_id), iid=start_range,
                                 values=(str(self.head_text), str(date_time), int(sensor_id), float(temperature)),
                                 tags=('low',))

            start_range += 1
            id_count += 1

        root.update()
        root.update_idletasks()
        self.tree.after(20000, self.update_window_table)


def main():
    window_unit()
    app1 = ModBus(1, 400, 1, 16)
    app1.connect_modbus()
    app1.table_insert(50, 10)
    app2 = ModBus(2, 400, 1, 16)
    app2.connect_modbus()
    app2.table_insert(50, 280)
    app3 = ModBus(3, 400, 1, 16)
    app3.connect_modbus()
    app3.table_insert(50, 550)
    app4 = ModBus(7, 110, 1, 16)
    app4.connect_modbus()
    app4.table_insert(450, 10)
    app5 = ModBus(8, 110, 1, 16)
    app5.connect_modbus()
    app5.table_insert(450, 280)
    mainloop()


if __name__ == '__main__':
    main()
