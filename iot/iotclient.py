import json
import glob
import os
import datetime,time
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
"""
  读取文件中与AWS连接配置信息加载
     到__Configaws_connect
"""
def Config_aws():
        x=glob.glob('/home/pi/megar/iot/*.json')
        f =open(x[0],"r")
        val=dict((json.loads(f.read())))
        print("AWS配置完成")    
        f.close()
        return val
class IotFuntion:

    """
        连接配置信息加载到AWS_SDK
        
    """ 
    def __init__(self,CallBack,Topic,Publish):
        baseReconnectQuietTimeSecond = 1
        maxReconnectQuietTimeSecond  = 32
        stableConnectionTimeSecond   = 20
        # Drop the oldest request in the queue
        DROP_OLDEST = 0
        # Drop the newest request in the queue
        DROP_NEWEST = 1
        self.callback=CallBack
        self.topic=Topic
        self.publish=Publish
        self.AwsConfig =Config_aws()
        self.myMQTTClient=AWSIoTPyMQTT.AWSIoTMQTTClient(self.AwsConfig["clientid"])
        self.myMQTTClient.onOnline=self.callback["online"]
        self.myMQTTClient.onOffline=self.callback["offline"]
        self.myMQTTClient.configureEndpoint(self.AwsConfig["ioturl"],
                                            self.AwsConfig["port"]
                                           )
        self.myMQTTClient.configureCredentials(self.AwsConfig["pem"],
                                               self.AwsConfig["key"],
                                               self.AwsConfig["crt"]
                                              )                                 
        self.myMQTTClient.configureAutoReconnectBackoffTime(baseReconnectQuietTimeSecond,
                                                            maxReconnectQuietTimeSecond ,
                                                            stableConnectionTimeSecond
                                                           )
        self.myMQTTClient.configureOfflinePublishQueueing(30,DROP_NEWEST)# Infinite offline Publish queueing
        self.myMQTTClient.configureDrainingFrequency(2)          # Draining: 2 Hz
        self.myMQTTClient.configureConnectDisconnectTimeout(5)   # 5 sec
        self.myMQTTClient.configureMQTTOperationTimeout(5)       # 5 sec


    #遗言
    def configwill(self,num):
            dev=self.__loadS(num)
            self.myMQTTClient.configureLastWill(dev,"I wail......",1)

    #断开连接
    def Iot_disconnect(self):
        self.myMQTTClient.disconnectAsync(ackCallback=self.callback["disconnect"])
        time.sleep(1)
        # self.myMQTTClient.disconnect()      
     # 连接至IOT
    def Iot_connect(self):
        print("IOT_异步连接开始......")
        self.myMQTTClient.connectAsync(keepAliveIntervalSecond=2,ackCallback = self.callback["connect"]) 
    """
     订阅主题标题装载
    """
    def __loadS(self,num):
       return self.AwsConfig["re_mg"]["env"]+"/"+self.AwsConfig["re_mg"]["tenantId"]+"/"+self.AwsConfig["re_mg"]["clientId"]+"/"+self.topic[num]["topic"]
    """
        推送主题标题装载
    """
    def __loadP(self,num):
        return self.AwsConfig["re_mg"]["env"]+"/"+self.AwsConfig["re_mg"]["tenantId"]+"/"+self.AwsConfig["re_mg"]["clientId"]+"/"+self.publish[num]["topic"]       
    """
        配置订阅主题
    """     
    def Iot_topic(self,num):
        topic=self.__loadS(num)
        numid=self.myMQTTClient.subscribeAsync(topic,1,ackCallback=self.callback["subscribe"],
                                                  messageCallback=self.topic[num]["callname"]
                                              )
        if numid>0:
            pass
            # return (numid,dev)
        else:
            raise Exception("IOT订阅失败或无效")                                      
        # print(numid)                                              
    def Iot_Untopic(self,num):
        topic=self.__loadS(num)
        numid=self.myMQTTClient.unsubscribeAsync(topic,ackCallback=self.callback["unsubsribe"])   
        #  print(numid)
    """
     向主题推送消息
    """
    def Iot_Publish(self,num,date):
        topic=self.__loadP(num)
        numid=self.myMQTTClient.publishAsync(topic,date,1,self.publish[num]["callname"])
        if numid>0:
            pass
            # return (numid,dev)
        else:
            raise Exception("IOT推送失败或无效")

def netinit_iot():
    while 1:
        val = os.system("curl members.3322.org/dyndns/getip")
        if val!=0:
                print("等待网络就绪......",datetime.datetime.now())
        else:
                print("网 络 以 就 绪......",datetime.datetime.now())
                break

