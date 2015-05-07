# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 09:12:17 2013

@author: pi
"""
from flask import render_template
from threading import Thread
from pymodbus.server.sync import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from threading import Timer
import logging
import os
import time
import piface.pfio as pfio
from flask import Flask
app = Flask(__name__)
pfio.init()

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

counter=0
if os.path.exists("/var/contaimpulsi/counter.txt"):
    f=open("/var/contaimpulsi/counter.txt","r")
    counter=int(f.readline())
    f.close()

pulsetime=0
print str(counter)

@app.route('/hello/')
@app.route('/hello/<name>')

def hello(name=None):
    return render_template('hello.html',name=name)

    

def read_temp():
    while(1):
#        tfile=open("/sys/bus/w1/devices/28-000003eba319/w1_slave")
#        lines=tfile.read()
#        tfile.close()
#        print lines
#        time.sleep(1)
        f=open("/sys/bus/w1/devices/28-000003eba319/w1_slave")
        lines=f.readlines()
        f.close()
        print (lines)
        time.sleep(1)
#    while lines[0].strip()[-3:] != "YES":
#        time.sleep(0.2)
#    equals_pos = lines[1].find("t=")
#    if equals_pos != -1:
#        temp_string = lines[1][equals_pos+2:]
#        temp_c = float(temp_string)/1000.0
#        return temp_c
#    while True:    
#        print (read_temp()) 
#        time.sleep(1)

def updating_writer(context):

    f=open("/var/contaimpulsi/counter.txt", "r")
    b=int(f.readline())
    f.close()
    print("updating the context")
    register = 3
    slave_id = 0
    address  = 0x00  
    print ("new values: " + str(b))
    context[0].setValues(register, address, [b])
    t = Timer(5.0, updating_writer, args=[context])
    t.start()


def serverup():
    store = ModbusSlaveContext(
        di = ModbusSequentialDataBlock(0, 0),
        co = ModbusSequentialDataBlock(0, 0),
        hr = ModbusSequentialDataBlock(0, 0),
        ir = ModbusSequentialDataBlock(0, 0))
    context = ModbusServerContext(slaves=store, single=True)

    updating_writer(context)

#---------------------------------------------------------------------------# 
# initialize the server information
#---------------------------------------------------------------------------# 
# If you don't set this or any fields, they are defaulted to empty strings.
#---------------------------------------------------------------------------# 
    identity = ModbusDeviceIdentification()
    identity.VendorName  = 'Pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl   = 'http://github.com/bashwork/pymodbus/'
    identity.ProductName = 'Pymodbus Server'
    identity.ModelName   = 'Pymodbus Server'
    identity.MajorMinorRevision = '1.0'

    StartTcpServer(context, identity=identity, address=("10.10.10.91", 5020))

def contaimpulsi():
    
    pulsetime=0
    counter=0
    if os.path.exists("/var/contaimpulsi/counter.txt"):
        f=open("/var/contaimpulsi/counter.txt","r")
        counter=int(f.readline())
        f.close()
        
    while(1):
    
        if pfio.digital_read(4):
            pulsetime=pulsetime+1
        
        else:
            if pulsetime > 4:
            
                counter=counter+1
                pfio.digital_write(0,1)
                print "Consumo computer sala riunioni: " +str(counter) + " Wh"
                f=open("/var/contaimpulsi/counter.txt","w")
                f.write(str(counter))
                f.close()
        
            pulsetime=0
    
        time.sleep(0.01)
        pfio.digital_write(0,0)

Thread(target=read_temp).start()
Thread(target=contaimpulsi).start()
Thread(target=serverup).start()
Thread(target=hello).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0')