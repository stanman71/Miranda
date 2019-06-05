import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import io
import base64

from app.components.file_management import GET_PATH


def BUILD_GRAPH(values_1, values_2 = "", values_3 = "", values_4 = "", values_5 = ""):

	try:
		x1_coordinates = values_1[0]
		y1_coordinates = values_1[1]
		graph_1_name   = values_1[2]
		
		try:
			x2_coordinates = values_2[0]
			y2_coordinates = values_2[1]
			graph_2_name   = values_2[2]
		except:
			x2_coordinates = None
	
		try:
			x3_coordinates = values_3[0]
			y3_coordinates = values_3[1]
			graph_3_name   = values_3[2]
		except:
			x3_coordinates = None	
	
		try:
			x4_coordinates = values_4[0]
			y4_coordinates = values_4[1]
			graph_4_name   = values_4[2]
		except:
			x4_coordinates = None		
	
		try:
			x5_coordinates = values_5[0]
			y5_coordinates = values_5[1]
			graph_5_name   = values_5[2]
		except:
			x5_coordinates = None		
			
			
		fig, ax = plt.subplots()

		ax.plot(x1_coordinates, y1_coordinates, label=graph_1_name)

		if x2_coordinates is not None:
			ax.plot(x2_coordinates, y2_coordinates, label=graph_2_name)

		if x3_coordinates is not None:
			ax.plot(x3_coordinates, y3_coordinates, label=graph_3_name)

		if x4_coordinates is not None:
			ax.plot(x4_coordinates, y4_coordinates, label=graph_4_name)

		if x5_coordinates is not None:
			ax.plot(x5_coordinates, y5_coordinates, label=graph_5_name)
			
		ax.xaxis.set_major_formatter(plt.NullFormatter())

		# Put a legend up current axis	
		plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.135),
				  ncol=3, fancybox=True, shadow=True)				
				
		plt.savefig(GET_PATH() + '/app/static/images/graph.png')
		plt.close()
		
		return True   
	
	except Exception as e:
		return ("Fehler in Graph: " + str(e))
