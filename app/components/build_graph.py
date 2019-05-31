import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import io
import base64

from app.components.file_management import GET_PATH


def BUILD_GRAPH(type, values_1, values_2 = "", values_3 = ""):

	try:
		x1_coordinates = values_1[0]
		y1_coordinates = values_1[1]
		
		try:
			x2_coordinates = values_2[0]
			y2_coordinates = values_2[1]
		except:
			x2_coordinates = None
	
		try:
			x3_coordinates = values_3[0]
			y3_coordinates = values_3[1]
		except:
			x3_coordinates = None	
			
		img = io.BytesIO()
		
		if type == "plot":    
			plt.plot(x1_coordinates, y1_coordinates)

			if x2_coordinates is not None:
				plt.plot(x2_coordinates, y2_coordinates)

			if x3_coordinates is not None:
				plt.plot(x3_coordinates, y3_coordinates)



		if type == "scatter":    
			plt.scatter(x_coordinates, y_coordinates)

			if y2_coordinates is not None:
				plt.scatter(x_coordinates, y2_coordinates)
				plt.fill_between(y_coordinates, y2_coordinates, color='grey', alpha='0.5')  




		plt.savefig(GET_PATH() + '/app/static/images/graph.png')
		plt.close()
		
		return True   
	
	except:
		return False
