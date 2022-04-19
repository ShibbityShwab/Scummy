import discord
import asyncio
import mysql.connector
from datetime import datetime

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def on_ready(self):
        print('Logged in as')
        print(self.user)
        print(self.user.id)
        print('------')
    
    async def my_background_task(self):
              
        await self.wait_until_ready()
        
        channel = self.get_channel(682102804097269917) # channel ID goes here
        
        #connect to db
        mydb = mysql.connector.connect(
            host="bloodshotstudios.com",
            user="bloodshotstudios_scumbot",
            password="DRBpSWB3eybeh2v!",
            database="bloodshotstudios_scum"
        )

        mycursor = mydb.cursor()
        
        while not self.is_closed():
            print("looped")
            if "lastRun" not in locals():
                mycursor.execute(f"""SELECT EventDate FROM RunLog WHERE ServiceType = 'DISCORD' ORDER BY EventDate DESC LIMIT 1""")
                lastRun = mycursor.fetchall()[0][0].strftime("%Y-%m-%d %H:%M:%S")

            mycursor.execute(f"""SELECT * FROM Death WHERE EventDate >= '{lastRun}'""")            
            newDeaths = mycursor.fetchall()
            
            for record in newDeaths:
                print(record)
                
                #await channel.send(f"""{record[3]} killed {record[5]} with a {record[6]}""")
                await channel.send(f"""\n **Killer:** \n{record[3]} **Victim:** \n{record[5]} **Weapon:** \n{record[6]}""")
                
            lastRun = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            mycursor.execute(f"""UPDATE RunLog SET EventDate = '{lastRun}' WHERE ServiceType = 'DISCORD'""")
            
            mydb.commit()
            
            await asyncio.sleep(300) # task runs every 60 seconds

client = MyClient( activity=discord.Game(name='SCUM'), intents=discord.Intents().default() )
client.run('OTY0NjM5OTUzNTE2NjM0MjAz.Ylnk9w.HZLTlvEZJCSOVQmwaERFzJzwoyQ')