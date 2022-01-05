import serial_a
import ctypes
import time

"""发送报文类型模板"""
Product_keyID=[0x00,0x68, 0x00, 0x42,0x41, 0x13, 0x00,0x00, 0x01,0x00,0x00]
Eve_getStatus = [0x00,0x6c, 0x05, 0x42,0x41,0x01,0x00,0x00,0x00,0x00]
Eve_getRequests = [0x00,0x6c, 0x05, 0x42,0x41,0x0c,0x00,0x00,0x00,0x00]
Eve_DOrinse=[0x00,0x68,0x00,0x42,0x41,0x03,0x00,0x00,0x00,0x00]
Polltime=0.05
"""read buff"""
Read_status=[]
Read_quse=[]
"""存一包完整的数据"""
Read_msg=[]
"""解析后数据存储"""
Read_par=[]
"""加密/解密转换参照码"""
__spe_chars=(0x00, 0x01, 0x02, 0x03, 0x04, 0x0a, 0x0d, 0x10, 0x17)
""" 加载CRC算法函数到python（C实现的CRC）"""
ll = ctypes.cdll.LoadLibrary
adder = ll('/home/pi/megar/coffee/crc16.so')

"""读数据装转换"""    
def str_0x(val):
    dat=[]
    for i in val:
        dat.append(int(i))
    return dat    
"""加密"""
def stuff(dats):
    payload=[]
    for dat in dats:
        if dat in __spe_chars:
            payload.append( 0x10 )
            payload.append( 0x40 + dat )
        else:
            payload.append( dat ) 
            
    return (payload)
""" 解密"""
def unStuff( dats ):
    i = 0
    payload=[]
    while i < len(dats):
        if dats[i] == 0x10:
            if (i + 1) < len(dats):
                if (dats[i+1]-0x40) in __spe_chars:
                    payload.append( dats[i+1]-0x40 )
                    i = i + 1
                else:
                    payload.append( dats[i])
            else:
                payload.append( dats[i])
                pass 
        else:
            payload.append( dats[i])
        i = i + 1
    return ( payload )
""" CRC校验计算"""
def Crc_val(dat):
    crc_val=0
    crc_h=0
    crc_l=0
    crc_val=adder.Crc_coffee(bytes(dat),len(dat))
    crc_h=crc_val>>8
    crc_l=crc_val&0xff
    return crc_h,crc_l

"""生成报文编号（1-255）"""
class PnNumber:
    def __init__(self):
        self.__Status=0
        self.__Rinse=0
        self.__Rquest=0
        self.__keyid=[]
        self.__keynum=[]
    def LoopPn(self,char,val=1):
        if char=="Key":
            if val in self.__keynum:
                indx=self.__keynum.index(val)
                if self.__keyid[indx]==256:
                    self.__keyid[indx]=0
                self.__keyid[indx]+=1
                return self.__keyid[indx]
            else:
                self.__keyid.append(0)
                self.__keynum.append(val)
                return 0
        elif char=="Status":
            if self.__Status==256:
                self.__Status=0
            self.__Status+=1
            return (self.__Status-1)     
        elif char== "Request":
            if self.__Rquest==256:
                self.__Rquest=0
            self.__Rquest+=1
            return (self.__Rquest-1)
        elif char== "Rinse":
            if self.__Rinse==256:
                self.__Rinse=0
            self.__Rinse+=1
            return (self.__Rinse-1)
PnObject=PnNumber()
"""咖啡机业务"""
class Eversys:
    def __init__(self,name,val):
        self.__bus=serial_a.Serialport(name,val)
        self.__bus.portopen()
        self.__data=list()
        self.__Rawdata=list()
    """装载数据pip-data段"""     
    def __pip_data(self,val):
       self.__data.clear()
       for i in val:
            self.__data.append(i)
    """装载校验直到数据包"""
    def __raw_data(self):
        self.__Rawdata.clear()
        crc_hl = Crc_val(self.__data)    
        self.__data.append(crc_hl[1])
        self.__data.append(crc_hl[0])
        self.__Rawdata=stuff(self.__data)
    """装载数据包头尾"""
    def __pask(self):
        self.__Rawdata.insert(0,0x01)
        self.__Rawdata.append(0x04)
    """装载数据帧 参考设备手册帧字节含义"""    
    def __addpask(self,val):
       self.__pip_data(val)
       self.__raw_data()
       self.__pask()
    def Evesend(self,val):
       self.__addpask(val)
       self.__bus.write(self.__Rawdata)
    """读取数据"""
    def Everead(self):
        return str_0x(self.__bus.read())
    """清理暂存变量"""
    def __cleardata_q(self):
        global Read_quse
        Read_quse.clear()
    def __cleardata_s(self):
        global Read_status
        Read_status.clear()
    def __cleardata_m(self):
        global Read_msg
        Read_msg.clear()    
    """ 读设备返回数据加装到全局变量"""
    def addpack(self):
        global Read_status
        data_val=self.Everead()
        # if len(Read_status)>84:
        #     self.__cleardata_s()
        if len(data_val)>0:
            for i in data_val:
                Read_status.append(i)
    """提取一包完整的数据 True 取到一包 Flase 未取到"""
    def fetchdata(self):
        global Read_quse
        global Read_status
        global Read_msg
        while len(Read_status)>0:
            if Read_status[0]==0x04:
                Read_quse.append(Read_status.pop(0))
                Read_msg=unStuff(Read_quse)
                self.__cleardata_q()
                return True 
            Read_quse.append(Read_status.pop(0))   
        return False
    #Demolition head and tail,crc
    def Unpackingcrc(self):
        global Read_msg
        crc_l=Read_msg [-3]
        crc_h=Read_msg [-2]
        Read_msg.pop(0)
        # print(crc_h,crc_l)
        for i in range(3):
            Read_msg.remove(Read_msg[-1])
        crc_hl = Crc_val(Read_msg)
        # print(crc_h==crc_hl[0],crc_h==crc_hl[1])
        if crc_l==crc_hl[1] and crc_h==crc_hl[0]:
            return True
        else:
            return False
    """将设备状态，咖啡状态，牛奶状态，KEY状态"""       
    def UnpackStatus(self):
        global Read_msg
        global Read_par
        setbit=(10,11,15,16,21,22)
        for i in setbit:
            Read_par.append(Read_msg[i])    
    """返回设备是否开始清洗标志位"""
    def UnpackRinse(self):
        global Read_msg
        global Read_par 
        Read_par=[Read_msg[-1]]
    """应答解析处理"""
    def ack(self):
        ACK=(0x01,0x00,0x6a,0x41,0x42,0x04)
        global Read_msg
        if len(Read_msg)==7:
            Read_msg.pop(3)
            for i in range(len(Read_msg)-1):
                if Read_msg[i]!=ACK[i]:
                    return False
            self.__cleardata_m()    
            return True
        else:
            return False    
    """拆包设备状态返回（status/Rinse）"""    
    def Analyticalstatus(self):
        global Read_msg
        global Read_status
        """设备状态""" 
        # print("rev"+str(Read_msg))
        if len(Read_msg)==34:
            
            if self.Unpackingcrc():
                self.UnpackStatus()
                
                return True
            else: 
                return False
        elif len(Read_msg)==15:
            if self.Unpackingcrc():
                self.UnpackRinse() 
                return True
            else:
                return False
        else:
            return False
        self.__cleardata_m()     
                     
    """ char :不同数据包编号区分"key","Status","Request","Rinse", keyID:产品编号"""
    def Keysend(self,char,keyID):
        global Product_keyID
        pndata=PnObject.LoopPn(char,keyID)
        # print("key"+str(pndata))
        Product_keyID[2]=pndata
        Product_keyID[-1]=keyID
        #key send data
        self.Evesend(Product_keyID)
        time.sleep(Polltime)
    """设备状态获取"""
    def Statsend(self,char):
        global Thrdcommunication
        global Eve_getStatus
        pndata=PnObject.LoopPn(char)
        print("status "+str(pndata))
        Eve_getStatus[2]=pndata
        self.Evesend(Eve_getStatus)
        time.sleep(Polltime)
    """清洗状态获取请求 """
    def Rquestsend(self,char):
        global Thrdcommunication
        global Eve_getRequests
        pndata=PnObject.LoopPn(char)
        Eve_getRequests[2]=pndata
        self.Evesend(Eve_getRequests)
        time.sleep(Polltime)
    """清洗执行发送请求"""
    def Rinsesend(self,char):
        global Thrdcommunication
        global Eve_DOrinse
        pndata=PnObject.LoopPn(char)
        Eve_DOrinse[2]=pndata
        self.Evesend(Eve_DOrinse)
        time.sleep(Polltime)
# val=Eversys("/dev/ttyUSB0",115200)
# val.Keysend("Key",0x02)
# val.Keysend("Key",0x01)
# val.Keysend("Key",0x01)
# val.Keysend("Key",0x01)
# val.Keysend("Key",0x01)
# val.Keysend("Key",0x01)
# val.Keysend("Key",0x01)
# val.Keysend("Key",0x01)
# val.Keysend("Key",0x01)
# val.Keysend("Key",0x01)
# val.Rinsesend("Rinse")
# val.Statsend("Status")
# val.Statsend("Status")
# val.Rquestsend("Request")
# val.Rquestsend("Request")
# # val.Rinsesend("Rinse")
# val.Statsend("Status")
# val.Statsend("Status")
# val.Rquestsend("Request")
# val.Rquestsend("Request")
# val.Statsend("Status")
# val.Statsend("Status")
# val.Statsend("Status")
# val.Statsend("Status")

# while 1:
#    val.addpack()
#    if val.fetchdata():
#        print("end") 
#        if val.ack():
#           print("ack")
#        if val.Analyticalstatus():
#            print("read "+str(Read_par))
#            Read_par.clear()

#   """
#     读机制
#     循环读 addpack(self)
#     取一包数据 fetchdata(self）
#     应答判断  ack(self)
#     状态与清洗状态 Analyticalstatus(self):
#              设备状态  CRC if Unpackingcrc():
#                             self.UnpackStatus() 
#              是否开始清洗状态  CRC if Unpackingcrc():
#                             self.UnpackRinse()
#     最终状态值，Read_par  用完后clear                                      
                       
#   """



         