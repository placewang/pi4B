import datetime
# ON/off status
NetStatus=False

#连接回调
def __myconnack_callback(mid,data):
    if mid=="CONNECTED":
         ConnectStatus=True
         print("OK_connect_IOT",datetime.datetime.now())
    else:
        raise Exception("connect_IOT_fail",datetime.datetime.now())
#断开回调
def __mydisconnect_callback(mid,data):
    if mid=="DISCONNECTED":
        print("dis_connect_IOT",datetime.datetime.now())
#订阅主题回调
def __mySubackCallback(mid,data):
    print("Topic_ackcall  "+str(mid))
#取消订阅回调       
def __myUnsubackCallback(mid):
    print("Untopic_callback "+str(mid))

#主题消息接收回调
def __myTopic01(client, userdata, message):
    print(message.topic)
    print(message.payload)
def __myTopic02(client, userdata, message):
    print(message.topic)
    print(message.payload)
def __myTopic03(client, userdata, message):
    print(message.topic)
    print(message.payload)
def __myTopic04(client, userdata, message):
    print(message.topic)
    print(message.payload)     
#将新消息异步发布到所需主题回调
def __myPublish01(mid):
    print("Publish01_callback "+str(mid))
    pass
def __myPublish02(mid):
    print("Publish02_callback "+str(mid))
    pass
def __myPublish03(mid):
    print("Publish03_callback "+str(mid))
    pass
def __myPublish04(mid):
    print("Publish04_callback "+str(mid))
    pass 
#设备在线/离线
def __myOnOnlineCallback():
    global NetStatus
    NetStatus=True
    print("")
    print("设备上线",datetime.datetime.now())
    print("")
def __myOnOfflineCallback():
    global NetStatus
    NetStatus=False
    print("")
    print("网络掉线中.......",datetime.datetime.now())
    print("")
IotCallback_dict={
    "connect":__myconnack_callback,

    "disconnect":__mydisconnect_callback,

    "subscribe":__mySubackCallback,

    "unsubsribe":__myUnsubackCallback,

    "online":__myOnOnlineCallback,

    "offline":__myOnOfflineCallback
}

Topic_list=[
    {
        "topic":"123",
        "callname":__myTopic01
    },
    {
        "topic":"456",
        "callname":__myTopic02
    },
    {
        "topic":"789",
        "callname":__myTopic03
    },
    {
        "topic":"abc",
        "callname":__myTopic04
    }
]
Publish_list=[
    {
        "topic":"789",
        "callname":__myPublish01
    },
    {
        "topic":"456",
        "callname":__myPublish02
    },
    {
        "topic":"123",
        "callname":__myPublish03
    },
    {
        "topic":"abc",
        "callname":__myPublish04
    }
]