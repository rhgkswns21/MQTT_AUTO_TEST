import datetime as date
import paho.mqtt.client as mqtt
import os
import time
import threading

f = open('E:\MyFolder\Source\Python\PycharmProjects\External Data\mqtt_info\mqtt_info.txt', 'r')

PANID = "0X0006"
M = "353041080746073"
# S1 = "353041080754218"
S1 = None
S2 = None
S3 = None

sample_count = 5
fail_sample_count = 0
ok_sample_count = 0

check_device = [False, False, False, False ]

broker = f.readline()
mqtt_topic = f.readline()
file_path = f.readline().strip()
f.close()


def timer01():
    print('timer01')

def sample_start():
    client.publish("Entity/SHM/Node/" + PANID + "/OTA", '{"nId":"' + PANID + '","nT":"SHM","status":{"OP":"Sample"},"timestamp":' + str(int(time.time())) + '}')
    for i in range(0,4):
        check_device[i] = False
    print("sample start", check_device)
    if M == None:
        check_device[0] = True
    if S1 == None:
        check_device[1] = True
    if S2 == None:
        check_device[2] = True
    if S3 == None:
        check_device[3] = True
    print("CheckDiveice init", check_device)
    threading.Timer(120, timer01).start()

def log_start():
    if M != None:
        client.publish("Entity/SHM/Node/"+M+"/OTA",'{"nId":"'+M+'","nT":"SHM","status":{"OP":"TestLog"},"timestamp":'+str(int(time.time()))+'}')
    if S1 != None:
        client.publish("Entity/SHM/Node/"+S1+"/OTA",'{"nId":"'+S1+'","nT":"SHM","status":{"OP":"TestLog"},"timestamp":'+str(int(time.time()))+'}')
    if S2 != None:
        client.publish("Entity/SHM/Node/"+S2+"/OTA",'{"nId":"'+S2+'","nT":"SHM","status":{"OP":"TestLog"},"timestamp":'+str(int(time.time()))+'}')
    if S3 != None:
        client.publish("Entity/SHM/Node/"+S3+"/OTA",'{"nId":"'+S3+'","nT":"SHM","status":{"OP":"TestLog"},"timestamp":'+str(int(time.time()))+'}')
    client.disconnect()

def on_connect(client, userdata, flags, rc):
    print ("Connected with result coe " + str(rc))
    if M != None:
        client.subscribe('Entity/SHM/Node/'+M+'/Device/Status')
    if S1 != None:
        client.subscribe('Entity/SHM/Node/'+S1+'/Device/Status')
    if S2 != None:
        client.subscribe('Entity/SHM/Node/'+S2+'/Device/Status')
    if S3 != None:
        client.subscribe('Entity/SHM/Node/'+S3+'/Device/Status')

# 서버에게서 PUBLISH 메시지를 받을 때 호출되는 콜백
def on_message(client, userdata, msg):
    global ok_sample_count
    mqtt_data = str(msg.payload)
    topic = str(msg.topic)
    if topic.find(M):
        if (mqtt_data.find('"GENERIC') >= 0):
            print("Master GENERIC")
            check_device[0] = True
    elif topic.find(S1):
        if (mqtt_data.find('"GENERIC') >= 0):
            print("Slave01 GENERIC")
            check_device[1] = True
    elif topic.find(S2):
        if (mqtt_data.find('"GENERIC') >= 0):
            print("Slave02 GENERIC")
            check_device[2] = True
    elif topic.find(S3):
        if (mqtt_data.find('"GENERIC') >= 0):
            print("Slave03 GENERIC")
            check_device[3] = True

    if False in check_device:
        print("list False")
    else:
        print("list True", check_device)
        ok_sample_count += 1
        print("Sample count : ", ok_sample_count)
        if(ok_sample_count >= sample_count):
            log_start()
        else:
            sample_start()

def on_log (client, userdata, level, buf) :
    print ( date.datetime.now(), "log :", buf)

client = mqtt.Client()        # MQTT Client 오브젝트 생성

client.on_log = on_log
client.on_message = on_message   # on_message callback 설정
client.on_connect = on_connect     # on_connect callback 설정
client.connect(broker.strip())   # MQTT 서버에 연결

sample_start()

client.loop_forever()