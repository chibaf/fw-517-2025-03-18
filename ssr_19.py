import RPi.GPIO as GPIO
from time import sleep
import time
import sys
import os
import datetime

ont=float(sys.argv[1])
offt=float(sys.argv[2])

ssr_pin=19
gid=str(ssr_pin)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(ssr_pin,GPIO.OUT)

f=open("ssr"+gid+"_log.txt",'a',encoding="utf-8")
t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, 'JST')
now = datetime.datetime.now(JST)
d = now.strftime('%Y %m %d %H:%M:%S')
s1=d+": ssr_"+gid+" "+str(ont)+" "+str(offt)+" starts\n"
f.write(s1)
f.close()

path = './go'+gid+'.txt'

while True:
  try:
	  is_file = os.path.isfile(path)
	  if is_file:
	    print("find go"+gid+".txt\n")
	  else:
	    print("stop this proram")
	    f=open("ssr_"+gid+"_log.txt",'a',encoding="utf-8")
	    t_delta = datetime.timedelta(hours=9)
	    JST = datetime.timezone(t_delta, 'JST')
	    now = datetime.datetime.now(JST)
	    d = now.strftime('%Y %m %d %H:%M:%S')
	    s1=d+": ssr_"+gid+" "+str(ont)+" "+str(offt)+" stops\n"
	    f.write(s1)
	    f.close()
	    GPIO.output(ssr_pin, 0)
	    exit()
	  GPIO.output(ssr_pin, 1)
	  print("SSR "+gid+" ON ("+str(ont)+"sec)\n")
	  time.sleep(ont)
	  if offt != 0.0:
	    GPIO.output(ssr_pin, 0)
	    print("SSR "+gid+" OFF ("+str(offt)+"sec)\n")
	    time.sleep(offt)
  except KeyboardInterrupt:
    print("stop this proram")
    f=open("ssr"+gid+"_log.txt",'a',encoding="utf-8")
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    d = now.strftime('%Y %m %d %H:%M:%S')
    s1=d+": ssr_"+gid+" "+str(ont)+" "+str(offt)+" stops\n"
    f.write(s1)
    f.close()
    GPIO.output(ssr_pin, False)
    exit()
  
