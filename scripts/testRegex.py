import re
import io

with open("login_20220413130043.log", 'rb') as fh:
    buf = io.BytesIO(fh.read())

testString = "2022.04.13-20.51.39: '73.101.142.72 76561198276735120:Simen(4)' logged in"

testPattern = "(?P<timestamp>\d{4}.\d{2}.\d\d-\d\d.\d\d.\d\d): '(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}) (?P<steamid>\d*):(?P<name>.*)\((?P<playerid>\d+)\)' (?P<status>logged in)"

print("Loop over buffer and search each string: \n")
for line in buf.getvalue().decode('utf-16-le').splitlines(True):
    print(f"PLAIN: {line}")
    print(f"SEARCHED: {re.search(testPattern, line)}")
    print(len(line.strip()))
    print(ascii(line))
    print(len(testString))
    print(ascii(testString))
    print("\n")
    if line == testString:
        print("STRING MATCH /n")
    
print(re.findall(testPattern, buf.getvalue().decode('utf-16-le')))

print("test string for a base line: \n")
print(testString)
testOutput = re.search(testPattern, testString)

print(testOutput)


