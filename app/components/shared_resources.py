import datetime
import time
import threading

process_management_queue = []


# mqtt_incoming_messages

mqtt_incoming_messages_list = []

def REFRESH_MQTT_INPUT_MESSAGES_THREAD():

	while True:
		
		Thread = threading.Thread(target=REFRESH_MQTT_INPUT_MESSAGES)
		Thread.start()  
		  
		time.sleep(1)


def REFRESH_MQTT_INPUT_MESSAGES():   
	
	try:

		# get the time check value
		time_check = datetime.datetime.now() - datetime.timedelta(seconds=60)
		time_check = time_check.strftime("%Y-%m-%d %H:%M:%S")

		for message in mqtt_incoming_messages_list:

			time_message = datetime.datetime.strptime(message[0],"%Y-%m-%d %H:%M:%S")   
			time_limit   = datetime.datetime.strptime(time_check, "%Y-%m-%d %H:%M:%S")

			# remove saved message after 60 seconnds
			if time_message <= time_limit:
				mqtt_incoming_messages_list.remove(message)

	except Exception as e:
		print(e)


# error_list_delete_mqtt_device

error_list_delete_mqtt_device = ""

def SET_ERROR_DELETE_MQTT_DEVICE(error_list):
	global error_list_delete_mqtt_device
	
	error_list_delete_mqtt_device = error_list
	
	
def GET_ERROR_DELETE_MQTT_DEVICE():
	global error_list_delete_mqtt_device
	
	return error_list_delete_mqtt_device


# spotify_authorization_header

spotify_authorization_header  = ""

def SET_SPOTIFY_AUTHORIZATION_HEADER(token):
	global spotify_authorization_header
	
	spotify_authorization_header = token
	
	
def GET_SPOTIFY_AUTHORIZATION_HEADER():
	global spotify_authorization_header
	
	return spotify_authorization_header
	
	
