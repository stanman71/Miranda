import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

matplotlib.rc('axes',edgecolor='white')

import io
import base64

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


from app.components.file_management import GET_PATH


def BUILD_GRAPH(df_sensors):

	try:
		x = df_sensors.index

		min_x = min(x)
		max_x = max(x)

		plt.xlim(min_x, max_x)

		selected_sensors = df_sensors['Sensor'].unique()

		# create a graph for every sensor
		try:
			graph_1 = df_sensors[df_sensors['Sensor'].isin([selected_sensors[0]])]
			label   = graph_1['Device'].unique() + ":" + graph_1['Sensor'].unique()
			
			plt.plot(graph_1.index, graph_1['Sensor_Value'].values, label=label[0])

		except:
			pass
		try:
			graph_2 = df_sensors[df_sensors['Sensor'].isin([selected_sensors[1]])]
			label   = graph_2['Device'].unique() + ":" + graph_2['Sensor'].unique()
			
			plt.plot(graph_2.index, graph_2['Sensor_Value'].values, label=label[0])
		except:
			pass
		try:
			graph_3 = df_sensors[df_sensors['Sensor'].isin([selected_sensors[2]])]
			label   = graph_3['Device'].unique() + ":" + graph_3['Sensor'].unique()
			
			plt.plot(graph_3.index, graph_3['Sensor_Value'].values, label=label[0])
		except:
			pass
		try:
			graph_4 = df_sensors[df_sensors['Sensor'].isin([selected_sensors[3]])]
			label   = graph_4['Device'].unique() + ":" + graph_4['Sensor'].unique()
			
			plt.plot(graph_4.index, graph_4['Sensor_Value'].values, label=label[0])
		except:
			pass
		try:
			graph_5 = df_sensors[df_sensors['Sensor'].isin([selected_sensors[4]])]
			label   = graph_5['Device'].unique() + ":" + graph_5['Sensor'].unique()
			
			plt.plot(graph_5.index, graph_5['Sensor_Value'].values, label=label[0])
		except:
			pass		
		try:
			graph_6 = df_sensors[df_sensors['Sensor'].isin([selected_sensors[5]])]
			label   = graph_6['Device'].unique() + ":" + graph_6['Sensor'].unique()
			
			plt.plot(graph_6.index, graph_6['Sensor_Value'].values, label=label[0])
		except:
			pass
		try:
			graph_7 = df_sensors[df_sensors['Sensor'].isin([selected_sensors[6]])]
			label   = graph_7['Device'].unique() + ":" + graph_7['Sensor'].unique()
			
			plt.plot(graph_7.index, graph_7['Sensor_Value'].values, label=label[0])
		except:
			pass			
		try:
			graph_8 = df_sensors[df_sensors['Sensor'].isin([selected_sensors[7]])]
			label   = graph_8['Device'].unique() + ":" + graph_8['Sensor'].unique()
			
			plt.plot(graph_8.index, graph_7['Sensor_Value'].values, label=label[0])
		except:
			pass	
		try:
			graph_9 = df_sensors[df_sensors['Sensor'].isin([selected_sensors[8]])]
			label   = graph_9['Device'].unique() + ":" + graph_9['Sensor'].unique()
			
			plt.plot(graph_9.index, graph_9['Sensor_Value'].values, label=label[0])
		except:
			pass	
	

		# change color
		plt.grid(color='white', linestyle='-', linewidth=0.25, alpha=0.5)
		plt.tick_params(colors='white')


		# format legent
		leg = plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.185),
						 ncol=2, fancybox=True)
		leg.get_frame().set_alpha(0.1)	
						
		for text in leg.get_texts():
			plt.setp(text, color = 'white')
		

		plt.gcf().autofmt_xdate()
				
		plt.savefig(GET_PATH() + '/app/static/images/graph.png', transparent=True)
		plt.close()
		
		return True   
	
	except Exception as e:
		return ("Fehler in der Grapherstellung: " + str(e))

