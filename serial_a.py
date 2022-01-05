import serial
import time
import binascii
import base64
import serial.tools.list_ports

class Serialport:
    """

      serial port open,close read write
    
    """
    __dev_usb=[]
    __name_devchar=["/dev/ttyUSB0","/dev/ttyUSB1","/dev/ttyUSB2","/dev/ttyUSB3","/dev/ttyAMA0"]
    def __init__(self,name,Baud=9600,bytesize=8,parity="N", stopbits=1,timeout=0):
       if len(list(serial.tools.list_ports.comports()) )>1 or name=="/dev/ttyAMA0":
           self.name=name
           self.__Baud=Baud
           self.__bytesize=bytesize
           self.__parity=parity
           self.__stopbits=stopbits
           self.__timeout=timeout
           Serialport.__dev_usb.append(name)
       else:
           raise Exception("not defind ttyUSB list number")
    @property
    def name(self):
        return self.__name
    @name.setter
    def name(self,val):
      if val in Serialport.__dev_usb:
         raise Exception("%s_Used"%(val))
      elif not val in Serialport.__name_devchar:
         raise Exception("%s-dev_notfind"%(val))  
      else:
           self.__name=val
    def portopen(self):
        self.__ser=serial.Serial(self.__name,self.__Baud,self.__bytesize,self.__parity,self.__stopbits,self.__timeout)
        self.__ser.flushInput()
        if self.__ser.isOpen():
           return True
        else:
           raise Exception("Failed to open port")
    def read(self):
    
        return self.__ser.read(84)
    
    def write(self,val):
        if type(val)==str:
            self.__ser.write(val.encode("utf-8"))
        else:
            self.__ser.write(val)
    def close(self):
        self.__ser.close()
    def __del__(self):
        self.close()
        Serialport.__dev_usb.remove(self.__name)
    

