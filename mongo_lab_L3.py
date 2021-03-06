import pandas as pd
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Modbus_Database"]
mycol = mydb["collection11"]

# data = pd.DataFrame(mycol.find({}, {'_id': 0}))
data = pd.DataFrame(
    mycol.find({"Sensor Type No": "3"}, {'_id': 0}))

data.to_csv('Lab_Data_L3.csv')

read_file = pd.read_csv(r'Lab_Data_L3.csv')
read_file.to_excel(r'Lab_Data_Excel_L3.xlsx', index=None, header=True)
