import datetime as date
import paho.mqtt.client as mqtt
import os
import time
import threading

Device = []
device_type = ["M", "S1", "S2", "S3"]
check_device = [False, False, False, False]
timer = []

f = open("info.txt", "r")
broker = f.readline()
sample_count = int(f.readline().strip())
PANID = f.readline().strip()
for i in range(4):
    check_str = f.readline().strip()
    if check_str:
        Device.append(check_str)
        print("ok : " + check_str)
    else:
        Device.append(None)

ok_sample_count = 0
try_count = 0
f.close()

## mqtt get timeout 일정시간 등록된 디바이스에서 메시지를 받지 못하면 발생.
def timer01():
    global try_count
    print("data get timeout")
    try_count += 1
    f = open('log.txt', 'a')
    f.writelines(str(date.datetime.now()) + "\t" + "Sample no : " + "\t" + str(try_count) + "\n")
    for i in range(len(Device)):
        if check_device[i] == False:
            log_txt = str(date.datetime.now()) + "\t" + "fail device : " + "\t" + device_type[i] +" " + Device[i] + "\n"
            print(log_txt)
            f.writelines(log_txt)
    f.close()
    sample_start()

def sample_start():
    print("Sample no : ", try_count)
    client.publish("Entity/SHM/Node/" + PANID + "/OTA", '{"nId":"' + PANID + '","nT":"SHM","status":{"OP":"Sample"},"timestamp":' + str(int(time.time())) + '}')
    for i in range(0, 4):
        check_device[i] = False
    print("sample start", check_device)

    for i in range(len(check_device)):
        if Device[i] == None:
            check_device[i] = True

    print("CheckDiveice init", check_device)

    time_list = threading.Timer(180, timer01)
    timer.append(time_list)
    time_list.start()

def log_start():
    for i in Device:
        if i != None:
            time.sleep(1)
            client.publish("Entity/SHM/Node/"+i+"/OTA",'{"nId":"'+i+'","nT":"SHM","status":{"OP":"TestLog"},"timestamp":'+str(int(time.time()))+'}')
    f = open('log.txt', 'a')
    f.writelines(str(date.datetime.now()) + "\t" + str(try_count - sample_count) + " is failed out of " + str(try_count) + " times\n")
    f.writelines(str(date.datetime.now()) + "\t" + "End Test...\n")
    f.close()
    client.disconnect()

def on_connect(client, userdata, flags, rc):
    print ("Connected with result coe " + str(rc))
    for i in Device:
        if i != None:
            time.sleep(1)
            client.subscribe('Entity/SHM/Node/'+i+'/Device/Status')

# 서버에게서 PUBLISH 메시지를 받을 때 호출되는 콜백
def on_message(client, userdata, msg):
    global ok_sample_count
    global try_count
    mqtt_data = str(msg.payload)
    topic = str(msg.topic)
    for i in range(len(Device)):
        if Device[i] != None:
            if(topic.find(Device[i]) >= 0):
                if(mqtt_data.find('"GENERIC"') >= 0):
                    print(Device[i] + "  GENERIC")
                    check_device[i] = True

    if False in check_device:
        print("list False")
    else:
        print("list True", check_device)
        for work in timer:
            work.cancel()
        ok_sample_count += 1
        try_count += 1
        if(ok_sample_count >= sample_count):
            log_start()
        else:
            time.sleep(1)
            sample_start()

def on_log (client, userdata, level, buf) :
    print ( date.datetime.now(), "log :", buf)

client = mqtt.Client()          # MQTT Client 오브젝트 생성

client.on_log = on_log          # on_log callback 설정
client.on_message = on_message  # on_message callback 설정
client.on_connect = on_connect  # on_connect callback 설정
client.connect(broker.strip())  # MQTT 서버에 연결

f = open('log.txt', 'a')
f.writelines("\n" + str(date.datetime.now()) + "\t" +"Test Start...\n")
f.writelines(str(date.datetime.now()) + "\t" +"Test count" + "\t" + str(sample_count) + "\n")
f.writelines(str(date.datetime.now()) + "\t" +"PANID" + "\t" + PANID + "\n")
for i in range(len(Device)):
    log_txt = str(date.datetime.now()) + "\t" + device_type[i] + "\t" + str(Device[i]) + "\n"
    f.writelines(log_txt)
f.close()

sample_start()

client.loop_forever()

print("Complete!")

# 라인 정지
a = input()