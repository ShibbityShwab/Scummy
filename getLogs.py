from ftplib import FTP
from stopwatch import Stopwatch
import io
import re
import requests
import mysql.connector
from datetime import datetime
import json

# host and credentials
host = "107.155.124.138"
port = 8821
username = ""
password = ""

# update dynamic dns
requests.get('')

#connect to db
mydb = mysql.connector.connect(
  host="",
  user="",
  password="",
  database=""
)

mycursor = mydb.cursor()

# source time of last run top avoid duplicates
if "lastRun" not in locals():
    mycursor.execute(f"""SELECT EventDate FROM RunLog WHERE ServiceType = 'LOGS' ORDER BY EventDate DESC LIMIT 1""")
    lastRun = mycursor.fetchall()[0][0]

# establing conneciton
timer = Stopwatch()
timer.start()
ftp = FTP()
ftp.connect(host, port)
ftp.login(username, password)
ftp.cwd("/107.155.124.138_7000/")
timer.stop()

print(f"CONNECTING TO FTP: {timer.elapsedTime()} \n")

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


# close buffers
adminLog.close()
chatLog.close()
deathLog.close()
loginLog.close()
minesLog.close()
violationsLog.close()

# close db connection
mydb.close()
