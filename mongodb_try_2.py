import pymongo
import csv

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Modbus_Database"]
mycol = mydb["collection7"]

cursor = mycol.find({"$and": [{"Sensor Type No": "1"}, {"Sensor No": "1"}]}, {'_id': 0})

outfile = open("asdxk.csv", "w")

# get a csv writer
writer = csv.writer(outfile)

# write data
# [writer.writerow(x) for x in cursor]
for x in cursor:
    writer.writerow(cursor)
