import pandas as pd
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Modbus_Database"]
mycol = mydb["collection7"]

# data = pd.DataFrame(mycol.find({}, {'_id': 0}))
data = pd.DataFrame(
    mycol.find({"Sensor Type No": "1"}, {'_id': 0}))

data.to_csv('Lab_Data_L1.csv')

read_file = pd.read_csv(r'Lab_Data_L1.csv')
read_file.to_excel(r'Lab_Data_Excel_L1.xlsx', index=None, header=True)
