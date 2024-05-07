import discord
import asyncio
import mysql.connector
import datetime

client = discord.Client(activity=discord.Game(name='SCUM'))
channel = client.get_channel()

# track runs to keep state
runLog = open("botRun.log", "r+")
lastRun = datetime.datetime.strptime(runLog.read(), '%Y-%m-%d %H:%M:%S.%f')
print(lastRun)
runLog.seek(0)
runLog.write(f"{datetime.datetime.utcnow()}")
runLog.truncate()
runLog.close()

#connect to db
mydb = mysql.connector.connect(
  host="",
  user="",
  password="",
  database=""
)

mycursor = mydb.cursor()

print(mydb)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

async def post_kill(record):
    await channel.send(f"{record[4]} killed {record[6]} with a {record[7]}")

client.run('')

while True:
    current_time = time.time()
    elapsed_time = current_time - start_time

    if elapsed_time > seconds:
        print("testing")
        mycursor.execute(
            f"""SELECT * FROM Death WHERE EventDate >= {lastRun}"""
        )
        
        myresult =  mycursor.fetchall()
        
        for record in myresult:
            kill_feed(record)
        break
