import can, canopen
import os,time
                    
class Canbus:
    def __init__(self,canname,canbit):
        self.__canname=canname
        self.__canbit=canbit
        # 启动CAN
    def canstart(self):
        can_setup_command="sudo ip link set "+self.__canname+" up type can bitrate "+self.__canbit
        os.system(can_setup_command)
        #停止 
    def canstop(self):
        can_stop_command = "sudo ip link set " + self.__canname + " down"
        os.system(can_stop_command)    
"""Canopen业务"""
class CanOpenSocket(Canbus):
    def __init__(self, canname, canbit):
        super().__init__(canname, canbit)
        self.canstart()
        # 实例化CAN接口供CanOpen调用 
        self.network = canopen.Network()
        # 创建Canopen添加本地从站节点加载EDS
        self.node = canopen.RemoteNode(1, '/home/pi/megar/canbus/CANOPEN_ESS_C_V1.2.eds')

        self.network.add_node(self.node)
        # 以主站模式连接至总线,并将总线切换到预操作状态
        self.network.connect(channel='can0', bustype='socketcan')
        self.node.nmt.state='PRE-OPERATIONAL'
    def __Sdoinit(self):
        """ SDO
            模式：速度3，位置1  回零6
            电机状态：释放，使能
            细分：6400
            电流比例：20(0-150)
            位置：移动量（位置模式下写入）
            最大速度：5-3000r/min
            加速度：0-2000ms
            减速度:0-2000ms
            故障复位：0/1
            当前位置清零
            X0输入配置位原点触发
            回原点模式:24 z/29 f 
            回零后偏移量：(-1000000-1000000)
            回零速度：0-3000（120）r/min
            回零偏移速度：0-3000（60）r/min
        """
        self.dev_mode=self.node.sdo["Mode of operation"]
        self.dev_setsta=self.node.sdo["ControlWord"]  
        self.dev_subdivision=self.node.sdo["Func.ServoBasic.DivNums"] 
        self.dev_current=self.node.sdo["Func.Opearat.closecur_per"]
        self.dev_Location=self.node.sdo["target position"]
        self.dev_speed=self.node.sdo["posmode speed"]
        self.dev_Acceleration=self.node.sdo["accel time"]
        self.dev_decrease_speed=self.node.sdo["decel time"]
        self.dev_rsterror=self.node.sdo["Func.MotionPara.ErrReset"]
        self.dev_positionclear=self.node.sdo["Func.MotionPara.CurPulRest"]
        self.dev_ORG=self.node.sdo[0x2030][0x02]
        self.dev_homemode=self.node.sdo["homing method"]
        self.dev_homedeviation=self.node.sdo["home offset"]
        self.dev_homespeed=self.node.sdo[0x6099][0x01]
        self.dev_deviationspeed=self.node.sdo[0x6099][0x02]
        self.node.nmt.state="OPERATIONAL"

    def __Pdoinit(self):
        
        """ PDO
            设备状态 u16
            马达运行状态 u16
            驱动器故障代码 u16
        """
        self.node.tpdo.read()
        self.node.rpdo.read()
        self.node.tpdo[1].clear()
        self.node.tpdo[1].add_variable("StatusWord")
        self.node.tpdo[1].add_variable('Func.Monitor.MotorState')
        self.node.tpdo[1].add_variable('DSP Error Code')
        self.node.tpdo[1].add_variable(0x2003)

        self.node.tpdo[1].trans_type = 254
        self.node.tpdo[1].event_timer = 0
        self.node.tpdo[1].enabled = True
        self.node.tpdo.save()
   
        # self.node.rpdo[1]['StatusWord'].phys = 1000
        # self.node.rpdo[1]['Func.Monitor.InStateGroup1'].phys = 1000
        # self.node.rpdo[1].start(0.1)
    """电机使能"""
    def start(self):
        self.dev_setsta.write(0x07)
        self.dev_setsta.write(0x0f)
    """初始化电机配置（PDO，SDO）"""    
    def motor1_init(self):
        self.__Pdoinit()
        self.__Sdoinit()
        self.dev_setsta.write(0x00)
        self.dev_setsta.write(0x06)
        self.dev_current.write(0x10)
        self.dev_Acceleration.read()
    """配置电机模式运动参数"""
    def motorcofig(self,mode=1,Pu=0x04):
            
            self.dev_subdivision.write(Pu)
            time.sleep(0.01)
            self.dev_Location.write(6400)
            self.dev_speed.write(120)
            self.dev_Acceleration.write(100)
            self.dev_decrease_speed.write(100)
            self.dev_setsta.write(0x4f)
            time.sleep(0.01)
            self.dev_setsta.write(0x5f)
            time.sleep(0.01)
            self.dev_mode.write(mode)
    """电机移动"""
    def motor_mov(self,modex=0x01,movnum=0):
        self.dev_Location.write(movnum)
        time.sleep(0.01)
        self.dev_mode.write(modex)
    """电机回零"""    
    def motor_home(self,modeh=0x01):
        self.dev_mode.write(modeh)
    '''故障复位'''    
    def motor_rset(self):
        self.dev_rsterror.write(1)
        self.dev_rsterror.write(0)
 
val=CanOpenSocket("can0","500000")
val.motor1_init()
val.start()
val.motorcofig()
print(val.dev_speed.read())
# val.dev_setsta.write(0x00)
# val.start()
# val.Pumcofig()
# val.Pum_mov(1,500000)
# print(val.dev_Location.read())
# time.sleep(8)
# val.Pum_Rset()






