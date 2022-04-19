import mysql.connector

lastRun = '2022-04-17 06:03:09'

#connect to db
mydb = mysql.connector.connect(
  host="bloodshotstudios.com",
  user="bloodshotstudios_scumbot",
  password="DRBpSWB3eybeh2v!",
  database="bloodshotstudios_scum"
)

mycursor = mydb.cursor()

print(mydb)

mycursor.execute(f"""SELECT * FROM Death""")
        
myresult =  mycursor.fetchall()

print(myresult)

for record in myresult:
    print(record)
    print(f"{record[4]} killed {record[6]} with a {record[7]}")
    print(type(record))