import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import io
import base64

from app.components.file_management import GET_PATH


def BUILD_GRAPH(df_sensors):

	try:
		x = df_sensors.index

		min_x = min(x)
		max_x = max(x)

		plt.xlim(min_x, max_x)

		selected_sensors = df_sensors['Sensor'].unique()

		try:
			graph_1 = df_sensors[df_sensors['Sensor'].isin([selected_sensors[0]])]
			plt.plot(graph_1.index, graph_1['Sensor_Value'].values, label=selected_sensors[0])

		except:
			pass
		try:
			graph_2 = df_sensors[df_sensors['Sensor'].isin([selected_sensors[1]])]
			plt.plot(graph_2.index, graph_2['Sensor_Value'].values, label=selected_sensors[1])
		except:
			pass
		try:
			graph_3 = df_sensors[df_sensors['Sensor'].isin([selected_sensors[2]])]
			plt.plot(graph_3.index, graph_3['Sensor_Value'].values, label=selected_sensors[2])
		except:
			pass
		try:
			graph_4 = df_sensors[df_sensors['Sensor'].isin([selected_sensors[3]])]
			plt.plot(graph_4.index, graph_4['Sensor_Value'].values, label=selected_sensors[3])
		except:
			pass
		try:
			graph_5 = df_sensors[df_sensors['Sensor'].isin([selected_sensors[4]])]
			plt.plot(graph_5.index, graph_5['Sensor_Value'].values, label=selected_sensors[4])
		except:
			pass		
		try:
			graph_6 = df_sensors[df_sensors['Sensor'].isin([selected_sensors[5]])]
			plt.plot(graph_6.index, graph_6['Sensor_Value'].values, label=selected_sensors[5])
		except:
			pass
		try:
			graph_7 = df_sensors[df_sensors['Sensor'].isin([selected_sensors[6]])]
			plt.plot(graph_7.index, graph_7['Sensor_Value'].values, label=selected_sensors[6])
		except:
			pass			
		try:
			graph_8 = df_sensors[df_sensors['Sensor'].isin([selected_sensors[7]])]
			plt.plot(graph_8.index, graph_7['Sensor_Value'].values, label=selected_sensors[7])
		except:
			pass	
		try:
			graph_9 = df_sensors[df_sensors['Sensor'].isin([selected_sensors[8]])]
			plt.plot(graph_9.index, graph_9['Sensor_Value'].values, label=selected_sensors[8])
		except:
			pass	
	
	
		plt.xlabel('x')
		plt.ylabel('y')
		plt.gcf().autofmt_xdate()

		plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.135),
				   ncol=3, fancybox=True, shadow=True)				
				
		plt.savefig(GET_PATH() + '/app/static/images/graph.png')
		plt.close()
		
		return True   
	
	except Exception as e:
		return ("Fehler in der Grapherstellung: " + str(e))

