import json
import requests
import os
"""

"""
#HTTP
url="https://api.dev.aiot.aws.megarobo.tech/device"
#注册信息
register_msg={
   
    "deviceName":"devpi_00",
    
    "tenantId":"wangdongchuan",
    
    "model":"AgrissaT1",
    
    "sn":"megar20210720000012"
    }
#IOT连接配置信息
config_file={
        "ioturl":"aw1nu4wbx9q7b.ats.iot.cn-north-1.amazonaws.com.cn",
        "port":8883,
        "pem":"/home/pi/megar/iot/AmazonRootCA1.pem",
        "key":"/home/pi/megar/iot/Privatekey.pem.key",
        "crt":"/home/pi/megar/iot/Certificate.pem.crt"
    }
# 注册接口
def register(date):
    re=requests.post(url,json=date)
    message=str(re.content,"utf-8")
    dev_mg=eval(message)
    if dev_mg["code"]==200 and dev_mg["msg"]=="设备注册成功":
       print("....code",dev_mg["code"],dev_mg["msg"]+"....")
    else:
        print("设备注册失败")
        print(dev_mg)
        return None
    pem=open("Certificate.pem.crt","w")
    pem.write(dev_mg["obj"]["certPem"])
    pem.close()
    print("  ......证书下载完成......")
    pri=open("Privatekey.pem.key","w")
    pri.write(dev_mg["obj"]["priKey"])
    pri.close()
    print("  ......私钥下载完成......")
    return dev_mg
#生成AWS连接时所需的配置文件
def confile(msg):
    global config_file
    date_file={
        "clientid":msg["obj"]["clientId"],
        "re_mg":{
                 "deviceId":msg["obj"]["deviceId"],
                 "deviceName":msg["obj"]["deviceName"],
                 "clientId":msg["obj"]["clientId"],
                 "tenantId":msg["obj"]["tenantId"],
                 "env":msg["obj"]["env"],
                 "model":msg["obj"]["model"],
                 "sn":msg["obj"]["sn"],
                 "status":msg["obj"]["status"]
                 }
               }
    config_file.update(date_file)
    config=open(msg["obj"]["sn"]+".json","w")
    config.write(json.dumps(config_file))
    config.flush()
    config.close()
    print("....AWS_connectcongfig_OK....")
#判断IOT注册信息是否完成
def Equipment_validation():
    file_name=("Privatekey.pem.key","Certificate.pem.crt")
    num=0
    for i in range(len(file_name)):
        if os.path.isfile(file_name[i]):
            print("文件"+file_name[i]+"以存在")
            num+=1
    if num>0:
        print("再次注册无效")
        return None
    else:
        return True
if __name__=="__main__":
   if Equipment_validation():
      dev_mg=register(register_msg)
      if not dev_mg:
        exit()
      elif type(dev_mg)==dict:    
        confile(dev_mg)
   else:
        exit()
    
    