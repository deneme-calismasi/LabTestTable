import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Modbus_Database"]
mycol = mydb["collection7"]

for x in (mycol.find({"Sensor No": "1"}, {'_id': 0})):
    print(x)
