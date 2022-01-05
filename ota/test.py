import json
import time
import os
import threading
from queue import Queue
import requests
import cryptography.exceptions
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

device = {}
myMQTTClient = None
# 是否可以取消升级
def init_mqtt_client(device):
    global myMQTTClient
    myMQTTClient = AWSIoTMQTTClient(device["client_id"])
    myMQTTClient.configureEndpoint("aw1nu4wbx9q7b.ats.iot.cn-north-1.amazonaws.com.cn", 8883)
    myMQTTClient.configureCredentials("E:/thing_ca/AmazonRootCA1.pem",
                                      "{}/private.pem.key".format(device["path"]),
                                      "{}/certificate.pem.crt".format(device["path"]))
    myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
    myMQTTClient.connect()
    print("连接成功")
    return myMQTTClient

def verify_sign(file, signature_info):
    # 取业务数据和签名
    signature = base64.b64decode(signature_info['signature'])
    # Load the public key.
    with open('public.key', 'rb') as f:
        public_key = load_pem_public_key(f.read(), default_backend())
    # Perform the verification.
    try:
        public_key.verify(
            signature,
            file,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        print("验签通过")
    except cryptography.exceptions.InvalidSignature as e:
        print('ERROR: Payload and/or signature files failed verification!')
        raise e
# 验证文件是否被修改
def valid_file(file_url, file_name, signature_info):
    print(file_url)
    r = requests.get(file_url)
    # open打开excel文件，报存为后缀为xls的文件
    fp = open(file_name, "wb")
    fp.write(r.content)
    fp.close()
    file = open(file_name, "rb").read()
    verify_sign(file, signature_info)
# 发送消息
def push_message(client, ota_id, status, msg):
    print("发送消息: {}".format(msg))
    payload = {
        "status": status,
        "msg": msg
    }
    client.publish(device["ota_report_topic"].format(device["env"],device["tenant_id"],device["client_id"],ota_id),
                         json.dumps(payload), 0)
# 开始ota升级
def start_ota(client, device, message_json, queue):
    ota_id = message_json["state"]["desired"]["ota"]["ota_id"]
    try:
        print("开始验证升级包")
        valid_file(message_json["state"]["desired"]["ota"]["url"], message_json["state"]["desired"]["ota"]["fileName"],
                   message_json["state"]["desired"]["ota"]["sign_package_signature_info"])
    except Exception as e:
        # print(e)
        push_message(client, ota_id, "REJECTED", "安装包被修改, 拒绝升级")
        # raise ValueError("安装包被修改, 拒绝升级")
    print("验证文件通过, 开始升级")
    if queue.empty():
        queue.put(0, "start")
        push_message(client, ota_id, "IN_PROGRESS", "验证文件通过, 开始升级")
    else:
        result = queue.get()
        if result == "stop":
            print(result)
            print("停止升级")
            return
    print("开始升级, 不可再取消")
    time.sleep(10)
    # 设备状态模拟
    if device.__contains__("result_status") and device["result_status"] and device["result_status"]["status_list"]:
        status_list = device["result_status"]["status_list"]
        for s in status_list:
            push_message(client, ota_id, s, "模拟状态__{}".format(s))
            time.sleep(device["result_status"]["intervals"])
    else:
        # 开始升级
        push_message(client, ota_id, "SUCCEEDED", "升级完成")
        print("升级完成")

# 根据ota的状态, 处理消息
def ota_handler(client, message_json, queue):
    print(message_json)
    all_status = ["QUEUED", "IN_PROGRESS", "SUCCEEDED", "FAILED", "REJECTED", "CANCELED", "CANCELED_FAILED",
                  "CANCELED_SUCCEEDED"]
    progress_status = ["QUEUED", "IN_PROGRESS", "CANCELED_FAILED"]
    end_status = ["SUCCEEDED", "FAILED", "REJECTED", "CANCELED_SUCCEEDED"]
    status = message_json["state"]["desired"]["ota"]["status"]
    ota_id = message_json["state"]["desired"]["ota"]["ota_id"]
    if end_status.__contains__(status):
        print("ota升级状态为_{}_的升级任务结束, 不需要处理".format(status))
    elif status == "CANCELED":
        print(device)
        if queue.empty():
            # 获取离线时, 需要处理的消息
            queue.put("stop")
            push_message(client, ota_id, "CANCELED_SUCCEEDED", "取消完成")
        else:
            print("不能取消")
            push_message(client, ota_id, "CANCELED_FAILED", "已经开始升级, 不可取消")
    elif progress_status.__contains__(status):
        time.sleep(10)
        start_ota(client, device, message_json, queue)


class CallbackContainer(object):
    def __init__(self, client):
        self._client = client
        self.queue = Queue()
    def messagePrint(self, client, userdata, message):
        print("Received a new message: ")
        print(message.payload)
        print("from topic: ")
        print(message.topic)
        print("--------------\n\n")
    def messageForward(self, client, userdata, message):
        message_json = json.loads(message.payload.decode())
        if message_json["state"].__contains__("desired"):
            print("收到消息, 创建新的线程处理")
            # 创建新的线程, 开始执行任务
            threading.Thread(target=ota_handler, args =(self._client, message_json, self.queue)).start()
        else:
            print("消息发送成功")
    def pubackCallback(self, mid):
        print("Received PUBACK packet id: ")
        print(mid)
        print("++++++++++++++\n\n")
    def subackCallback(self, mid, data):
        print("Received SUBACK packet id: ")
        print(mid)
        print("Granted QoS: ")
        print(data)
        print("++++++++++++++\n\n")



def connect_device(device):
    myMQTTClient = init_mqtt_client(device)
    myCallbackContainer = CallbackContainer(myMQTTClient)
    myMQTTClient.subscribe(
        "$aws/things/{}/shadow/name/ota/update/accepted".format(device["client_id"]), 1, myCallbackContainer.messageForward)
    myMQTTClient.subscribe("$aws/things/{}/shadow/name/ota/get/accepted".format(device["client_id"]),
                           0, myCallbackContainer.messageForward)
    print("订阅成功")
    # 获取离线时, 需要处理的消息
    myMQTTClient.publish("$aws/things/{}/shadow/name/ota/get".format(device["client_id"]), "", 0)
    print("获取离线消息: ")
    while True:
        pass

if __name__ == '__main__':
    device = {
        "client_id" : "DEV_42cd58429fb445b391f67eef0d1efacd",
        "path": "E:\\workspace\\megaX\\iot\\aws-iot-device-simulator\\thing_ca\ota",
        "env": "DEV",
        "tenant_id": "weicheng",
        "ota_report_topic": "{}/{}/{}/ota/{}/reported",
        # "result_status": {
        #     "status_list": ["IN_PROGRESS", "CANCELED", "CANCELED_SUCCEEDED"],
        #     "intervals": 10
        # }
    }
    connect_device(device)
