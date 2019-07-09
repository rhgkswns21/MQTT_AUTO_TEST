import datetime as date
import paho.mqtt.client as mqtt
import os

f = open('E:\MyFolder\Source\Python\PycharmProjects\External Data\mqtt_info\mqtt_info.txt', 'r')

broker = f.readline()
mqtt_topic = f.readline()
file_path = f.readline().strip()
f.close()

# 서버에게서 PUBLISH 메시지를 받을 때 호출되는 콜백
def on_message(client, userdata, msg):
    now_time = str(date.datetime.now())
    # print("Time: ", now_time)
    # print("Topic: ", msg.topic)

def on_log (client, userdata, level, buf) :
    print ( date.datetime.now(), "log :", buf)

client = mqtt.Client()        # MQTT Client 오브젝트 생성

client.on_log = on_log
client.on_message = on_message   # on_message callback 설정
client.connect(broker.strip())   # MQTT 서버에 연결
client.subscribe(mqtt_topic.strip())

client.loop_forever()