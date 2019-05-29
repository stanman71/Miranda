import threading
import heapq


from app import app
from app.database.database import *
from app.components.control_scheduler import SCHEDULER_TIME_PROCESS, SCHEDULER_SENSOR_PROCESS, SCHEDULER_PING_PROCESS, GET_SUNRISE_TIME, GET_SUNSET_TIME
from app.components.control_controller import CONTROLLER_PROCESS


""" ################ """
"""  scheduler jobs  """
""" ################ """


from flask_apscheduler import APScheduler

scheduler = APScheduler()
scheduler.start()   


@scheduler.task('cron', id='update_sunrise_sunset', hour='*')
def update_sunrise_sunset():

	for task in GET_ALL_SCHEDULER_TASKS():

		if task.option_sunrise == "checked" or task.option_sunset == "checked":

			# get coordinates
			coordinates = GET_LOCATION_COORDINATES(task.location)

			if coordinates != "None" and coordinates != None: 

				# update sunrise / sunset
				SET_SCHEDULER_TASK_SUNRISE(task.id, GET_SUNRISE_TIME(float(coordinates[0]), float(coordinates[1])))
				SET_SCHEDULER_TASK_SUNSET(task.id, GET_SUNSET_TIME(float(coordinates[0]), float(coordinates[1])))
							

@scheduler.task('cron', id='scheduler_time', minute='*')
def scheduler_time():
   
	for task in GET_ALL_SCHEDULER_TASKS():
		if task.option_time == "checked" or task.option_sun == "checked":
			ADD_TASK_TO_PROCESS_MANAGEMENT(10, "time", task.id)
         

@scheduler.task('cron', id='scheduler_ping', second='0, 10, 20, 30, 40, 50')
def scheduler_ping():
   
	for task in GET_ALL_SCHEDULER_TASKS():
		if task.option_position == "checked":
			ADD_TASK_TO_PROCESS_MANAGEMENT(10, "ping", task.id)



""" ################ """
""" management queue """
""" ################ """

# https://www.bogotobogo.com/python/python_PriorityQueue_heapq_Data_Structure.php

process_management_queue = []


def ADD_TASK_TO_PROCESS_MANAGEMENT(priority, task_type, task_id, ieeeAddr = "", msg = ""):
	global process_management_queue
   
	heapq.heappush(process_management_queue, (priority, task_type, task_id, ieeeAddr, msg))


def PROCESS_MANAGEMENT_THREAD():
	global process_management_queue
   
	while True:
      
		try:
			process = heapq.heappop(process_management_queue)[1:]
			
			print(process)
         
			if process[0] == "time":
				task = GET_SCHEDULER_TASK_BY_ID(process[1])
				SCHEDULER_TIME_PROCESS(task)
			
			if process[0] == "sensor":
				task     = GET_SCHEDULER_TASK_BY_ID(process[1])
				ieeeAddr = process[2]
				SCHEDULER_SENSOR_PROCESS(task, ieeeAddr)    	         
         
			if process[0] == "ping":
				task = GET_SCHEDULER_TASK_BY_ID(process[1])
				SCHEDULER_PING_PROCESS(task)    
							  
			if process[0] == "controller":
				ieeeAddr = process[2]
				msg      = process[3]
				CONTROLLER_PROCESS(ieeeAddr, msg)    	         
			  
		except:
			pass
      
		time.sleep(0.25)
   
       
Thread = threading.Thread(target=PROCESS_MANAGEMENT_THREAD)
Thread.start() 
