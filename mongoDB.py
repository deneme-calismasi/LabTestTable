import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Modbus_Database"]
mycol = mydb["collection4"]

mycol.drop()
