import paho.mqtt.client as mqtt

BROKER_ADDRESS = "localhost"

def MQTT_START():
 
	def on_message(client, userdata, message):
		msg = str(message.payload.decode("utf-8"))
		print("message received: ", msg)
		print("message topic: ", message.topic)
	 
	def on_connect(client, userdata, flags, rc):
		client.subscribe('/SmartHome/data')

	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message
	 
	client.connect(BROKER_ADDRESS)
	 
	print("Connected to MQTT Broker: " + BROKER_ADDRESS)
	 
	client.loop_forever()


def MQTT_PUBLISH(MQTT_TOPIC, MQTT_MSG):

	def on_publish(client, userdata, mid):
		print ("Message Published...")

	client = mqtt.Client()
	client.on_publish = on_publish
	client.connect(BROKER_ADDRESS) 
	client.publish(MQTT_TOPIC,MQTT_MSG)
	client.disconnect()