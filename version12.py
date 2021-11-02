import math
from pyModbusTCP.client import ModbusClient
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import *
import tkinter
import pymongo
import datetime as dt


class ModBus:
    sensor_min_num = 0
    sensor_max_num = 2
    lineNo = 0
    sensorTypeNo = 0

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Sensor's Temperatures °C")
        self.root.geometry("480x630")
        self.root.grid()
        self.style = ttk.Style()
        self.style.map("Treeview", foreground=self.fixed_map("foreground"), background=self.fixed_map("background"))

    def sensor_nums(self, sensorTypeNo, lineNo, sensor_min_num, sensor_max_num):
        self.sensor_min_num = sensor_min_num
        self.sensor_max_num = sensor_max_num
        self.lineNo = lineNo
        self.sensorTypeNo = sensorTypeNo
        self.resultList = []
        self.regNoList = []
        self.reg_list = list(range(self.sensor_min_num, self.sensor_max_num + 1))

    def fixed_map(self, option):
        return [elm for elm in self.style.map("Treeview", query_opt=option) if elm[:2] != ("!disabled", "!selected")]

    #
    # def window_unit(self):
    #     self.root.title("Sensor's Temperatures °C")
    #     self.root.geometry("480x630")
    #     self.root.grid()

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

        value = [[num for num in range(1, 1 + self.regs_count)], self.reg_list, self.connect_modbus()]

        data = np.array(value).T.tolist()

        products = data
        self.arr = []
        for product in products:
            vals = {}
            vals["Sensor No"] = str(int(product[1]))
            vals["Temp"] = str(round(product[2], 4))
            vals["Time"] = str(dt.datetime.now().strftime('%Y-%m-%d %X'))
            self.arr.append(vals)
        return self.arr

    def record_mongo(self):
        lst = self.list_to_dict()
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["Modbus_Database"]
        mycol = mydb["collection4"]

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

        # self.window_unit()
        self.tree = ttk.Treeview(self.root)
        verscrlbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)

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

        start_range = 0
        id_count = 1

        for record in self.record_mongo()[-(self.regs_count):]:
            sensor_id = record[0]
            temperature = record[1]
            date_time = record[2]
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

        self.tree.after(60000, self.update_window_table)

    def update_window_table(self):

        for i in self.tree.get_children():
            self.tree.delete(i)

        start_range = 0
        id_count = 1

        for record in self.record_mongo()[-(self.regs_count):]:
            sensor_id = record[0]
            temperature = record[1]
            date_time = record[2]
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

        self.root.update()
        self.root.update_idletasks()
        self.tree.after(60000, self.update_window_table)


# if __name__ == "__main__":
#     app1 = ModBus(1, 2, 1, 5)
#     app1.table_insert(50, 100)
#     app2 = ModBus(2, 2, 1, 5)
#     app2.table_insert(100, 150)
#     app3 = ModBus(3, 2, 1, 5)
#     app3.table_insert(150, 200)
#     mainloop()


def main():  # run mianloop
    app = ModBus()
    app.sensor_nums(1, 2, 1, 5)
    app.table_insert(100, 150)


if __name__ == '__main__':
    main()
