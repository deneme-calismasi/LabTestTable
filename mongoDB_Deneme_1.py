import pandas as pd
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Modbus_Database"]
mycol = mydb["collection7"]

# data = pd.DataFrame(mycol.find({}, {'_id': 0}))
data = pd.DataFrame(
    mycol.find({"$or": [{"Sensor Type No": "1"}, {"Sensor Type No": "2"}, {"Sensor Type No": "3"}]}, {'_id': 0}))

data.to_csv('Lab_Data.csv')

read_file = pd.read_csv(r'Lab_Data.csv')
read_file.to_excel(r'Lab_Data_Excel.xlsx', index=None, header=True)
