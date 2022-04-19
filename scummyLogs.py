
import asyncio
import io
import json
import mysql.connector
import re
import requests
import time

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from ftplib import FTP

# regex patterns
loginPattern = re.compile(r"(?P<timestamp>\d{4}.\d{2}.\d\d-\d\d.\d\d.\d\d): '(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}) (?P<steamid>\d*):(?P<playername>.*)\((?P<playerid>\d+)\)' (?P<status>logged in)")
logoutPattern = re.compile(r"(?P<timestamp>\d{4}.\d{2}.\d\d-\d\d.\d\d.\d\d): '(?P<playerid>\d+)' (?P<status>logging out)")
chatPattern = re.compile(r"(?P<timestamp>\d{4}.\d{2}.\d\d-\d\d.\d\d.\d\d): '(?P<steamid>\d*):(?P<playername>.*)\((?P<playerid>\d+)\)' '(?P<room>\w+): (?P<message>.*)'")
deathPattern = re.compile(r"(?P<timestamp>\d{4}.\d{2}.\d\d-\d\d.\d\d.\d\d): Died: (?P<victim>.+) \((?P<victimid>\d+)\), Killer: (?P<killer>.+) \((?P<killerid>\d+)\) Weapon: (?P<weapon>.+) \[\w+\]")
killObjectPattern = re.compile(r"{.+[:,].+}|\[.+[,:].+\]")

# start buffers
adminLog = io.BytesIO()
chatLog = io.BytesIO()
deathLog = io.BytesIO()
loginLog = io.BytesIO()
minesLog = io.BytesIO()
violationsLog = io.BytesIO()

# update dynamic dns
requests.get('https://bloodshotstudios.com/cpanelwebcall/hmpmfjzbdxuaaofaneoeetpumofjnqkp')

#connect to db
mydb = mysql.connector.connect(
    host="bloodshotstudios.com",
    user="bloodshotstudios_scumbot",
    password="DRBpSWB3eybeh2v!",
    database="bloodshotstudios_scum"
)

mycursor = mydb.cursor()

async def getLogs():
    while True:
        # FTP credentials
        host = "107.155.124.138"
        port = 8821
        username = "logbot"
        password = "DRBpSWB3eybeh2v!"
        
        # FTP connection
        ftp = FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        ftp.cwd("/107.155.124.138_7000/")

        # loop over files in directory
        for file in ftp.nlst():

            if re.match("admin", file):
                ftp.retrbinary('RETR ' + file, adminLog.write)

            elif re.match("chat", file):
                ftp.retrbinary('RETR ' + file, chatLog.write)

            elif re.match("kill", file):
                ftp.retrbinary('RETR ' + file, deathLog.write)

            elif re.match("login", file):
                ftp.retrbinary('RETR ' + file, loginLog.write)

            elif re.match("mines", file):
                ftp.retrbinary('RETR ' + file, minesLog.write)

            elif re.match("violations", file):
                ftp.retrbinary('RETR ' + file, violationsLog.write)
        
        await asyncio.sleep(1)
        print("'getLogs' Task Executed")

async def parseLogs():
    while True:
        # source time of last run top avoid duplicates
        if "lastRun" not in locals():
            mycursor.execute(f"""SELECT EventDate FROM RunLog WHERE ServiceType = 'LOGS' ORDER BY EventDate DESC LIMIT 1""")
            lastRun = mycursor.fetchall()[0][0]

        # print buffers 
        for match in re.finditer(loginPattern, loginLog.getvalue().decode('utf-16-le')):
            if datetime.strptime(match.group('timestamp'), '%Y.%m.%d-%H.%M.%S') < lastRun:
                continue
            
            print(match.groupdict())
            
            mycursor.execute(
                f"""INSERT INTO Login (
                    EventDate,
                    IP,
                    SteamID,
                    PlayerName,
                    PlayerID
                ) VALUES (
                    "{match.group('timestamp')}",
                    "{match.group('ip')}",
                    {match.group('steamid')},
                    "{match.group('playername')}",
                    {match.group('playerid')}
                )"""
            )
            
        for match in re.finditer(logoutPattern, loginLog.getvalue().decode('utf-16')):
            if datetime.strptime(match.group('timestamp'), '%Y.%m.%d-%H.%M.%S') < lastRun:
                continue
            
            print(match.groupdict())
            
            mycursor.execute(
                f"""INSERT INTO Logout (
                    EventDate,
                    PlayerID
                ) VALUES (
                    "{match.group('timestamp')}",
                    {match.group('playerid')}
                )"""
            )
        
        for match in re.finditer(chatPattern, chatLog.getvalue().decode('utf-16-le')):
            if datetime.strptime(match.group('timestamp'), '%Y.%m.%d-%H.%M.%S') < lastRun:
                continue
            
            print(match.groupdict())
            
        for match in re.finditer(deathPattern, deathLog.getvalue().decode('utf-16-le')):
            if datetime.strptime(match.group('timestamp'), '%Y.%m.%d-%H.%M.%S') < lastRun:
                continue
            
            print(match.groupdict())
            
            mycursor.execute(
                f"""INSERT INTO Death (
                    EventDate,
                    KillerID,
                    Killer,
                    VictimID,
                    Victim,
                    Weapon
                ) VALUES (
                    "{match.group('timestamp')}",
                    {match.group('killerid')},
                    "{match.group('killer')}",
                    {match.group('victimid')},
                    "{match.group('victim')}",
                    "{match.group('weapon')}"
                )"""
            )

        # post update cleanup
        lastRun = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        mycursor.execute(f"""UPDATE RunLog SET EventDate = '{lastRun}' WHERE ServiceType = 'LOGS'""")

        mydb.commit()
        
        # flush buffers
        adminLog.flush()
        chatLog.flush()
        deathLog.flush()
        loginLog.flush()
        minesLog.flush()
        violationsLog.flush()
        
        # close db connection
        mydb.close()
        
        await asyncio.sleep(1)
        print("'parseLogs' Task Executed")

loop = asyncio.get_event_loop()
try:
    asyncio.ensure_future(getLogs())
    asyncio.ensure_future(parseLogs())
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    print("Closing Loop")
    loop.close()