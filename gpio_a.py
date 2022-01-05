import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
class Gpiout:
    """
    set,RST,GPIO
    """
    def __init__(self,*gpionum):
      self.__list_num =tuple()
      self.__GPIO_S = 0
      self.__GPIO_R = 1
      self.__list_val= set((4,5,6,12,13,17,27,22,26,18,23,24,25))
      if set(gpionum).issubset(self.__list_val):
          self.__list_num=gpionum  
          GPIO.setwarnings(False)
          GPIO.setup(list(gpionum),GPIO.OUT)
          GPIO.output(list(gpionum),self.__GPIO_R)
      else:
           raise IOError("gpio_objectinit_fail!")
        
    def setgpio(self,num):
        if num in self.__list_num:
            GPIO.output(num,self.__GPIO_S)
        else:
            raise IOError("gpiosetnum_fail!")
              
    def rstgpio(self,num):
        if num in self.__list_num:
            GPIO.output(num,self.__GPIO_R)
        else:
            raise IOError("gpiorstnum_fail!")
            
class Gpiput:
    """
     read GPIO status
    """
    def __init__(self,*gpionum):
      self.__list_num =tuple()
      self.__list_val= set((4,5,6,12,13,17,27,22,26,18,23,24,25))
      if set(gpionum).issubset(self.__list_val):
          self.__list_num=gpionum 
          GPIO.setwarnings(False)
          GPIO.setup(list(gpionum),GPIO.IN)
      else:
           raise IOError("gpio_object_input_init_fail!")
        
    def readgpio(self,num):
        if num in self.__list_num:
            if GPIO.input(num):
                return True
            else:
                return False
        else:
             raise IOError("gpio_readpin_fail!")
            