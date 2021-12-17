import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Modbus_Database"]
mycol = mydb["collection5"]

for x in mycol.find({}, {'_id': 0}):
    print(x)

# for x in mycol.find({}, {"_id": 0, "Sensor Type No": "8", "Line No": "110", "Sensor No": "16", "Temp": 1, "Time": 1}):
