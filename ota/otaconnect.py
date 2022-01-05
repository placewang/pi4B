import json
import glob
import time
import iot
import requests
import otack as ck
from iot.iotclient import IotFuntion 
from iot import callback as iotck
from iot.iotclient import netinit_iot

def ReadConfigAws():
    x=glob.glob('/home/pi/megar/iot/*.json')
    f =open(x[0],"r")
    val=dict((json.loads(f.read())))
    print("OTA配置中")    
    f.close()
    return val
class Ota_check(IotFuntion):
    def __init__(self,Ota_topic):
        super().__init__(iotck.IotCallback_dict,iotck.Topic_list,iotck.Publish_list)
        self.dev_config = ReadConfigAws()
        self.Ota_topic=Ota_topic
        
    """
     主题装载 0上报主题 1订阅
        num主题编号
        mg上报主题组成
    """
    def loadota(self,type,mg,num):
        
        if type:
            return self.dev_config["re_mg"]["env"]+"/"+\
                        self.dev_config["re_mg"]["tenantId"]+"/"+\
                            self.dev_config["re_mg"]["clientId"]+"/"+\
                                self.Ota_topic[num]["typ"] +mg+self.Ota_topic[num]["topic"] 
        else:
            return self.Ota_topic[num]["head"]+\
                        self.dev_config["re_mg"]["clientId"]+"/"+\
                            self.Ota_topic[num]["typ"]+self.Ota_topic[num]["topic"]
    """
       ota 配置订阅主题
    """     
    def OTA_topic(self,num,type=0,mg=None):
        topic=self.loadota(type,mg,num)
        numid=self.myMQTTClient.subscribeAsync(topic,0,ackCallback=self.Ota_topic[num]["subacall"],
                                                  messageCallback=self.Ota_topic[num]["callname"]
                                              )
    
        if int(numid)>0:
            pass
            # return (numid,dev)
        else:
            raise Exception("IOT订阅失败或无效")                                      
        print(numid)  
                                                    
    """
        取消配置订阅主题
    """ 
    def Ota_Untopic(self,num,type=0,mg=None):
        topic=self.loadota(type,mg,num)
        self.myMQTTClient.unsubscribeAsync(topic,ackCallback=self.Ota_topic[num]["unsubacall"])
    """
      向主题推送消息
    """
    def Ota_Publish(self,num,data,type=0,mg=None):
        topic=self.loadota(type,mg,num)
        numid=self.myMQTTClient.publishAsync(topic,data,1,self.Ota_topic[num]["callname"])
       
        if int(numid)>0:
            pass
        else:
            raise Exception("IOT推送失败或无效") 

if __name__=="__main__":
    # netinit_iot()
    Otadev = Ota_check(ck.Topic_list)
    Otadev.Iot_connect()
    time.sleep(2)
    Otadev.OTA_topic(0)
    Otadev.OTA_topic(1)
    time.sleep(2)
    Otadev.Ota_Publish(2,"")
    while 1:
        pass

