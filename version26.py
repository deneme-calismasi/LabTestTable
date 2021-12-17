import math
from pyModbusTCP.client import ModbusClient
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import *
import pymongo
import datetime as dt

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
        self.canvas = tk.Canvas(root, width=1580, height=600)

    def fixed_map(self, option):
        return [elm for elm in self.style.map("Treeview", query_opt=option) if elm[:2] != ("!disabled", "!selected")]

    def connect_modbus(self):
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
        return self.data_as_float

    def list_to_dict(self):
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

    def drag_start(self, event):
        widget = event.widget
        widget.startX = event.x
        widget.startY = event.y

    def drag_motion(self, event):
        widget = event.widget
        x = widget.winfo_x() - widget.startX + event.x
        y = widget.winfo_y() - widget.startY + event.y
        widget.place(x=x, y=y)

    def task_alert(self):
        circle = root.after(500, self.task_alert)
        if int(circle.split('#')[1]) % 2 == 0:
            self.canvas.itemconfig('rect9', fill='blue')
        else:
            self.canvas.itemconfig('rect9', fill='red')

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

        self.canvas.create_rectangle(10, 150, 1580, 170, fill='grey', outline='white', tag='rect1')
        self.canvas.create_rectangle(10, 500, 1580, 520, fill='grey', outline='white', tag='rect2')
        self.canvas.create_rectangle(365, 170, 385, 500, fill='grey', outline='white', tag='rect3')
        self.canvas.create_oval(1100, 240, 1300, 440, fill='blue', outline='white', tag='rect9')

        start3 = 45
        n = 1
        for z in range(26):
            self.canvas.create_text(start3, 140, text=n)
            self.canvas.create_text(start3, 530, text=n + 34)
            start3 += 60
            n += 1

        start4 = 195
        f = 27
        for t in range(8):
            self.canvas.create_text(395, start4, text=f)
            start4 += 40
            f += 1

        start_range = 0
        id_count = 1
        start = 40

        for record in self.record_mongo()[-(self.regs_count):]:
            sensor_id = record[2]
            temperature = record[3]
            date_time = record[4]
            if float(temperature) > 30.0:
                self.task_alert()
                self.tree.insert("", index='end', text="%s" % int(sensor_id), iid=start_range,
                                 values=(str(self.head_text), str(date_time), int(sensor_id), float(temperature)),
                                 tags=('high',))

                if sensor_id <= 26:
                    # ust cizgi
                    x_to_add = 60
                    y_lower, y_upper = 150, 170
                    if float(temperature) > 30.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='red', outline='white',
                                                     stipple='gray50', tag='rect4')
                    elif float(temperature) < 10.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='grey', outline='white',
                                                     stipple='gray50', tag='rect4')
                    elif float(temperature) < 0.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='black', outline='white',
                                                     stipple='gray50', tag='rect4')
                    else:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='blue', outline='white',
                                                     stipple='gray50', tag='rect4')
                    start += x_to_add

                    if sensor_id == 26:
                        start = 190

                elif 26 < sensor_id < 35:
                    y_to_add = 40
                    x_lower, x_upper = 365, 385
                    if float(temperature) > 25.0:
                        self.canvas.create_rectangle(x_lower, start, x_upper, start + 10, fill='red', outline='white',
                                                     stipple='gray50', tag='rect5')
                    elif float(temperature) < 10.0:
                        self.canvas.create_rectangle(x_lower, start, x_upper, start + 10, fill='grey', outline='white',
                                                     stipple='gray50', tag='rect5')
                    elif float(temperature) < 0.0:
                        self.canvas.create_rectangle(x_lower, start, x_upper, start + 10, fill='black', outline='white',
                                                     stipple='gray50', tag='rect5')
                    else:
                        self.canvas.create_rectangle(x_lower, start, x_upper, start + 10, fill='blue', outline='white',
                                                     stipple='gray50', tag='rect5')
                    start += y_to_add
                    if sensor_id == 34:
                        start = 40

                else:
                    # alt cizgi
                    x_to_add = 60
                    y_lower, y_upper = 500, 520
                    if float(temperature) > 30.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='red', outline='white',
                                                     stipple='gray50', tag='rect6')
                    elif float(temperature) < 10.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='grey', outline='white',
                                                     stipple='gray50', tag='rect6')
                    else:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='blue', outline='white',
                                                     stipple='gray50', tag='rect6')
                    start += x_to_add

            else:
                self.tree.insert("", index='end', text="%s" % int(sensor_id), iid=start_range,
                                 values=(str(self.head_text), str(date_time), int(sensor_id), float(temperature)),
                                 tags=('low',))

                if sensor_id <= 26:
                    # ust cizgi
                    x_to_add = 60
                    y_lower, y_upper = 150, 170
                    if float(temperature) > 30.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='red', outline='white',
                                                     stipple='gray50', tag='rect4')
                    elif float(temperature) < 10.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='grey', outline='white',
                                                     stipple='gray50', tag='rect4')
                    elif float(temperature) < 0.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='black', outline='white',
                                                     stipple='gray50', tag='rect4')
                    else:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='blue', outline='white',
                                                     stipple='gray50', tag='rect4')
                    start += x_to_add

                    if sensor_id == 26:
                        start = 190

                elif 26 < sensor_id < 35:
                    y_to_add = 40
                    x_lower, x_upper = 365, 385
                    if float(temperature) > 30.0:
                        self.canvas.create_rectangle(x_lower, start, x_upper, start + 10, fill='red', outline='white',
                                                     stipple='gray50', tag='rect5')
                    elif float(temperature) < 10.0:
                        self.canvas.create_rectangle(x_lower, start, x_upper, start + 10, fill='grey', outline='white',
                                                     stipple='gray50', tag='rect5')
                    elif float(temperature) < 0.0:
                        self.canvas.create_rectangle(x_lower, start, x_upper, start + 10, fill='black', outline='white',
                                                     stipple='gray50', tag='rect5')
                    else:
                        self.canvas.create_rectangle(x_lower, start, x_upper, start + 10, fill='blue', outline='white',
                                                     stipple='gray50', tag='rect5')
                    start += y_to_add
                    if sensor_id == 34:
                        start = 40

                else:
                    # alt cizgi
                    x_to_add = 60
                    y_lower, y_upper = 500, 520
                    if float(temperature) > 30.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='red', outline='white',
                                                     stipple='gray50', tag='rect6')
                    elif float(temperature) < 10.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='grey', outline='white',
                                                     stipple='gray50', tag='rect6')
                    elif float(temperature) < 0.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='black', outline='white',
                                                     stipple='gray50', tag='rect6')
                    else:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='blue', outline='white',
                                                     stipple='gray50', tag='rect6')
                    start += x_to_add

            start_range += 1
            id_count += 1

        self.tree.bind("<Button-1>", self.drag_start)
        self.tree.bind("<B1-Motion>", self.drag_motion)

        self.update_window_table()
        self.tree.after(60000, self.update_window_table)
        self.canvas.pack()

    def update_window_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        start_range = 0
        id_count = 1
        start = 40

        for record in self.record_mongo()[-(self.regs_count):]:
            sensor_id = record[2]
            temperature = record[3]
            date_time = record[4]
            if float(temperature) > 30.0:
                self.task_alert()
                self.tree.insert("", index='end', text="%s" % int(sensor_id), iid=start_range,
                                 values=(str(self.head_text), str(date_time), int(sensor_id), float(temperature)),
                                 tags=('high',))

                if sensor_id <= 26:
                    # ust cizgi
                    x_to_add = 60
                    y_lower, y_upper = 150, 170
                    if float(temperature) > 30.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='red', outline='white',
                                                     stipple='gray50', tag='rect4')
                    elif float(temperature) < 10.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='grey', outline='white',
                                                     stipple='gray50', tag='rect4')
                    elif float(temperature) < 0.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='black', outline='white',
                                                     stipple='gray50', tag='rect4')
                    else:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='blue', outline='white',
                                                     stipple='gray50', tag='rect4')
                    start += x_to_add

                    if sensor_id == 26:
                        start = 190

                elif 26 < sensor_id < 35:
                    y_to_add = 40
                    x_lower, x_upper = 365, 385
                    if float(temperature) > 25.0:
                        self.canvas.create_rectangle(x_lower, start, x_upper, start + 10, fill='red', outline='white',
                                                     stipple='gray50', tag='rect5')
                    elif float(temperature) < 10.0:
                        self.canvas.create_rectangle(x_lower, start, x_upper, start + 10, fill='grey', outline='white',
                                                     stipple='gray50', tag='rect5')
                    elif float(temperature) < 0.0:
                        self.canvas.create_rectangle(x_lower, start, x_upper, start + 10, fill='black', outline='white',
                                                     stipple='gray50', tag='rect5')
                    else:
                        self.canvas.create_rectangle(x_lower, start, x_upper, start + 10, fill='blue', outline='white',
                                                     stipple='gray50', tag='rect5')
                    start += y_to_add
                    if sensor_id == 34:
                        start = 40

                else:
                    # alt cizgi
                    x_to_add = 60
                    y_lower, y_upper = 500, 520
                    if float(temperature) > 30.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='red', outline='white',
                                                     stipple='gray50', tag='rect6')
                    elif float(temperature) < 10.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='grey', outline='white',
                                                     stipple='gray50', tag='rect6')
                    elif float(temperature) < 0.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='black', outline='white',
                                                     stipple='gray50', tag='rect6')
                    else:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='blue', outline='white',
                                                     stipple='gray50', tag='rect6')
                    start += x_to_add

            else:
                self.tree.insert("", index='end', text="%s" % int(sensor_id), iid=start_range,
                                 values=(str(self.head_text), str(date_time), int(sensor_id), float(temperature)),
                                 tags=('low',))

                if sensor_id <= 26:
                    # ust cizgi
                    x_to_add = 60
                    y_lower, y_upper = 150, 170
                    if float(temperature) > 30.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='red', outline='white',
                                                     stipple='gray50', tag='rect4')
                    elif float(temperature) < 10.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='grey', outline='white',
                                                     stipple='gray50', tag='rect4')
                    elif float(temperature) < 0.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='black', outline='white',
                                                     stipple='gray50', tag='rect4')
                    else:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='blue', outline='white',
                                                     stipple='gray50', tag='rect4')
                    start += x_to_add

                    if sensor_id == 26:
                        start = 190

                elif 26 < sensor_id < 35:
                    y_to_add = 40
                    x_lower, x_upper = 365, 385
                    if float(temperature) > 30.0:
                        self.canvas.create_rectangle(x_lower, start, x_upper, start + 10, fill='red', outline='white',
                                                     stipple='gray50', tag='rect5')
                    elif float(temperature) < 10.0:
                        self.canvas.create_rectangle(x_lower, start, x_upper, start + 10, fill='grey', outline='white',
                                                     stipple='gray50', tag='rect5')
                    elif float(temperature) < 0.0:
                        self.canvas.create_rectangle(x_lower, start, x_upper, start + 10, fill='black', outline='white',
                                                     stipple='gray50', tag='rect5')
                    else:
                        self.canvas.create_rectangle(x_lower, start, x_upper, start + 10, fill='blue', outline='white',
                                                     stipple='gray50', tag='rect5')
                    start += y_to_add
                    if sensor_id == 34:
                        start = 40

                else:
                    # alt cizgi
                    x_to_add = 60
                    y_lower, y_upper = 500, 520
                    if float(temperature) > 30.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='red', outline='white',
                                                     stipple='gray50', tag='rect6')
                    elif float(temperature) < 10.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='grey', outline='white',
                                                     stipple='gray50', tag='rect6')
                    elif float(temperature) < 0.0:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='black', outline='white',
                                                     stipple='gray50', tag='rect6')
                    else:
                        self.canvas.create_rectangle(start, y_lower, start + 10, y_upper, fill='blue', outline='white',
                                                     stipple='gray50', tag='rect6')
                    start += x_to_add

            start_range += 1
            id_count += 1

        root.update()
        root.update_idletasks()
        self.tree.after(60000, self.update_window_table)
        self.canvas.pack()


def main():
    window_unit()
    app1 = ModBus(1, 2, 400, 425)
    app1.connect_modbus()
    app1.table_insert(50, 10)
    app2 = ModBus(2, 2, 400, 425)
    app2.connect_modbus()
    app2.table_insert(50, 250)
    app3 = ModBus(3, 2, 400, 425)
    app3.connect_modbus()
    app3.table_insert(50, 490)
    mainloop()


if __name__ == '__main__':
    main()
