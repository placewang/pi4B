import json
#取消订阅回调       
def __myunSubackCkupdate(mid):
    print("OTA Untopic_ck update "+str(mid))
def __myunSubackckget_accepted(mid):
    print("OTA Untopic_ck get/accepted "+str(mid))
#OTA 订阅主题回调
def __mySubackCallbackupdate(mid,data):
    print("OTA Topic_ackcall update  "+str(mid))
def __mySubackckget_accepted(mid,data):
    print("OTA Topic_ackcall get_accepted "+str(mid))
#OTA订阅主题消息接收回调
def __myotacallbackupdate(client, userdata, message):
    print("OTA mgtopick update",str(message.topic))
    print(message.payload)
def __myotacallbackget_accepted(client, userdata, message):
    print("OTA mgtopick get/accepted",str(message.topic))
    print(json.loads(message.payload))
#OAT 将新消息异步发布到所需主题回调
def __myotaPubilishck_report(mid):
    print("OTA Pubilish ck ",str(mid))
def __myotaPubilishckget(mid):
    print("OTA Pubilish  ck get",str(mid))
  
Topic_list=[
    {
        "typ":"shadow/name/ota",
        "head":"$aws/things/",
        "topic":"/update/accepted",
        "subacall":__mySubackCallbackupdate,
        "unsubacall":__myunSubackCkupdate,
        "callname":__myotacallbackupdate
    },
    {
        "typ":"shadow/name/ota",
        "head":"$aws/things/",   
        "topic":"/get/accepted",
        "subacall": __mySubackckget_accepted,
        "unsubacall": __myunSubackckget_accepted,
        "callname":__myotacallbackget_accepted
    },
    # Report topic
    {
        "typ":"shadow/name/ota",
        "head":"$aws/things/",   
        "topic":"/get",
        "callname":__myotaPubilishckget
    },
    { 
        "topic":"/reported",
        "typ":"ota/",
        "callname":__myotaPubilishck_report
    }
]

# QUEUED              等待升级(云端指定的状态)
# IN_PROGRESS         开始升级(设备端发送状态)
# SUCCEEDED           升级成功(设备端发送状态)(终止状态)
# FAILED              升级失败(设备端发送状态)(终止状态)
# REJECTED            拒绝升级(设备端发送状态)(终止状态)
# CANCELED            取消升级(云端发送状态)
# CANCELED_FAILED     取消升级失败(设备端发送状态)
# CANCELED_SUCCEEDED  取消升级成功(设备端发送状态)(终止状态)