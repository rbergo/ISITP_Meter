"""
---------------------------------------
             iMonitor 
---------------------------------------

Progetto di monitoraggio della "Casa di Paglia". Una piccola struttura
in legno coibentata, che serve come modello di esempio per la misura 
dell'energia necessaria a mantenere un certo grado termico al suo interno.

Questo programma è un semplice Data Logger che registra un consumo di 
energia elettrica, letto da un power meter con emissione di impulsi,
e due temperature tramite sonde 1-wire, una interna e una esterna.

Classe 4 Elettronica anno 2014/2015
ISITP Verres (AO) - Italy
"""

from threading import Thread
from threading import Timer
import logging
import os
import time
import piface.pfio as pfio

def load_counter():
	"""
	Read the latest counter value stored on disk
	"""
	if os.path.exists("/var/log/iMeter/counter.dat"):
		f = open("/var/log/iMeter/counter.dat","r")
		counter = int(f.readline())
		f.close()
		return counter
	else
		return 0


def csv_log(counter, int_temp, ext_temp):
	"""
	Trace power meter measures on CSV file using SENECA file format
	INDEX;TYPE;TIMESTAMP;Var1;Var2;.....;VarN
	1;LOG;06/04/2015 21:00:00;1;2;....;100
	"""
	filename = "/var/spool/iMeter/CasaDiPaglia1_log",time.strftime("%Y%m%d"),"000000.csv"
	header = ""
	if not os.path.exists(filename):
		header = "INDEX;TYPE;TIMESTAMP;Energy;IntTemp;ExtTemp"
	f = open(filename,"w")
	if header != ""
		f.write(header)
	f.write("0;LOG;"time.strftime("%d/%m/%Y %H:%M:00"), ";", str(counter), ";", int_temp, ";", ext_temp)
	f.close()


def read_temp(Temp_ID):
	"""
	Web page: http://www.raspberrypi-spy.co.uk/2013/03/raspberry-pi-1-wire-digital-thermometer-sensor/
	Source: wget https://bitbucket.org/MattHawkinsUK/rpispy-misc/raw/master/python/ds18b20.py
	"""
	try:
		mytemp = ''
		filename = 'w1_slave'
		f = open('/sys/bus/w1/devices/' + Temp_ID + '/' + filename, 'r')
		line = f.readline() # read 1st line
		crc = line.rsplit(' ',1)
		crc = crc[1].replace('\n', '')
		if crc=='YES':
			line = f.readline() # read 2nd line
			mytemp = line.rsplit('t=',1)
		else:
			mytemp = 99999
		f.close()

		return int(mytemp[1])/float(1000)

	except:
		return 99999
	

def input_counter():
    
    pulsetime = 0
    while(1):
    
        if pfio.digital_read(4):
			#While HIGHT increment time counter
            pulsetime = pulsetime + 1
        
        else:
			#If the signal stay HIGH at least 50msec it's a good pulse
            if pulsetime >= 5:
                counter = counter + 1
                #pfio.digital_write(0,1)
                f = open("/var/log/iMeter/counter.dat","w")
                f.write(str(counter))
                f.close()
        
            pulsetime = 0
            
		#wait for 10msec
        time.sleep(0.01)
        #pfio.digital_write(0,0)

def main_loop():
	print "loop"
    t = Timer(60, csv_log, args=[counter, read_temp("28-000003eba319"), read_temp("28-000003eba319")])
    t.start()
	pass


pfio.init()

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

counter = load_counter()
print "Initial counter is ", str(counter)

Thread(target=input_counter).start()
Thread(target=main_loop).start()


