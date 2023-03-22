# Ronel Ethan T. Paguila - University of the Philippines Los Baños
# Github: ReethP
# Email: ret.paguila@gmail.com
# March 22,2023
# Version 1.0

# Recommandations:
# 		- Find a proper python to exe distribution so that users no longer need to install anaconda to run the program
# 		- Modularize the program or at least separate it into functions

import math
import copy
import inspect
from scipy.stats.mstats import winsorize

class Entry:
	def __init__(self,year,month,day,hour,ghi,dni,dhi,cloud_opacity):
		self.year = year
		self.month = month
		self.day = day
		self.hour = hour
		self.ghi = ghi
		self.dni = dni
		self.dhi = dhi
		self.cloud_opacity = cloud_opacity

	def __iter__(self):
		return iter([self.year, self.month, self.day, self.hour, self.ghi, self.dni, self.dhi,self.cloud_opacity])

class Day:
	def __init__(self,year,month,day,ghi,dni,dhi,cloud_opacity,index):
		self.year = year
		self.month = month
		self.day = day
		self.ghi = ghi
		self.dni = dni
		self.dhi = dhi
		self.cloud_opacity = cloud_opacity
		self.index = index
		self.distance = float("-inf")


def main():

	# Initialize arrays
	# removed data array in case user wants to view removed datapoints later down the line
	# complete entry array to be used in order to give a complete forecast later
	entry_array = []
	removed_data = []
	dhi_values = []
	day_array = []
	# K value is going to be 1 as we will simply find the closest day and base the forecast of the next 72 hours
	# on the next 72 hours AFTER the closest day
	k_value = 1
	counter = 0
	complete_entry_array = []


	################     START TRAINING     ################

	# open the necessary files
	training_file = open("data/training_weather_forecasting.csv","r")
	output_file = open("data/output.csv","w")
	

	# Headers for output CSV file
	header1 = ["Hour", "GHI", "DNI", "DHI", "Cloud Opacity"]
	header2 = ["Hour", "[W/m2]", "[W/m2]", "[W/m2]", "[%]"]

	# format header strings
	header1 = str(header1)
	header1 = header1.strip("[")
	header1 = header1.strip("]")
	header1 = header1.replace("\'","")

	header2 = str(header2)
	header2 = header2.strip("[")
	header2 = header2.strip("]")
	header2 = header2.replace("\'","")


	# Skip over to the more recent and relevant part of the data
	for line in training_file:
		line = line.strip("\n")
		line = line.split(",")

		# If you find the line with 2016, you append the line that the program currently is reading as it is the first datapoint
		if(line[0]=="2016"):
			line = list(map(float,line)) #splits the line, turns all values in the line into float, and turns it into a list
			entry_array.append(Entry(line[0],line[1],line[2],line[3],line[12],line[10],line[9],line[7]))			
			complete_entry_array.append(Entry(line[0],line[1],line[2],line[3],line[12],line[10],line[9],line[7]))

			# separate DHI value array as we will need it for winsorization later
			dhi_values.append(line[9])
			break
	# file pointer is now pointing at 2016 data (in case it is decided that the year the training data should start
	# in is 2016)

	# Read the rest of the training dataset and add the datapoints to entry_array as an Entry class 
	for line in training_file:
		line = line.strip("\n")
		line = list(map(float,line.split(",")))
		# Pre-processing step where we remove all datapoints with 0 DHI and DNI
		if(line[10] == 0 and line[9] == 0):
			removed_data.append(Entry(line[0],line[1],line[2],line[3],line[12],line[10],line[9],line[7]))
			complete_entry_array.append(Entry(line[0],line[1],line[2],line[3],line[12],line[10],line[9],line[7]))						
			continue
							#     year    month    day    hour     ghi      dni     dhi   cloud_opac
		entry_array.append(Entry(line[0],line[1],line[2],line[3],line[12],line[10],line[9],line[7]))
		complete_entry_array.append(Entry(line[0],line[1],line[2],line[3],line[12],line[10],line[9],line[7]))						
		dhi_values.append(line[9])


	# winsorization
	# 		                              0% bottom and 10% top
	cleaned_dhi_values = winsorize(dhi_values,(0.00,0.1))
	# replace DHI values of entries with cleaned DHI values (aka winsorized values)
	for iteration in range(len(entry_array)):
		entry_array[iteration].dhi = cleaned_dhi_values[iteration]

	# this is the part where we get the average values and create days
	dhi_values = []
	dni_values = []
	ghi_values = []
	cloud_opacity_values = []
	index = 0
	day_tracker = 1

	# for every hour in the data
	for entry in entry_array:
		# .append means add when the day changes get the average values of DHI, DNI, GHI, and Cloud Opacity
		if entry.day == day_tracker:
			dhi_values.append(entry.dhi)
			dni_values.append(entry.dni)
			ghi_values.append(entry.ghi)
			cloud_opacity_values.append(entry.cloud_opacity)
		else:
			dhi_average = sum(dhi_values)/len(dhi_values)
			dni_average = sum(dni_values)/len(dni_values)
			ghi_average = sum(ghi_values)/len(ghi_values)
			cloud_opacity_average = sum(cloud_opacity_values)/len(cloud_opacity_values)

			# Create a day entry using the average values throughout the day
			day_array.append(Day(entry.year,entry.month,entry.day,ghi_average,dni_average,dhi_average,cloud_opacity_average,index))
			# reset the arrays and make them empty for the next iteration
			dhi_values = []
			dni_values = []
			ghi_values = []
			cloud_opacity_values = []

			# add the current entry as it will then be the latest datapoint of the next day
			dhi_values.append(entry.dhi)
			dni_values.append(entry.dni)
			ghi_values.append(entry.ghi)
			cloud_opacity_values.append(entry.cloud_opacity)
			day_tracker = entry.day
			index+=1

	# do the following step one additional time as the condition only goes to the else statement on the change of a day
	dhi_average = sum(dhi_values)/len(dhi_values)
	dni_average = sum(dni_values)/len(dni_values)
	ghi_average = sum(ghi_values)/len(ghi_values)
	cloud_opacity_average = sum(cloud_opacity_values)/len(cloud_opacity_values)

	# Create a day entry using the average values throughout the day
	day_array.append(Day(entry.year,entry.month,entry.day,ghi_average,dni_average,dhi_average,cloud_opacity_average,index))


	#####################################     END OF TRAINING     #####################################

	#####################################     START OF TESTING    #####################################

	# Read the testing file composed of 24 hours worth of data. Change the file name into appropriate file name
	# For future files please follow the convention used in the input file
	day_file = open("data/testing_weather_forecasting.csv","r")
	day_entry_array = []

	# Same steps for the training dataset except this is done over 24 datapoints and turned into 1 day
	for line in day_file:
		line = line.strip("\n")
		line = line.split(",")
		if(line[0]!="Year"):
			line = list(map(float,line)) #splits the line, turns all values in the line into float, and turns it into a list
			day_entry_array.append(Entry(line[0],line[1],line[2],line[3],line[12],line[10],line[9],line[7]))			
			break

	for line in day_file:
		line = line.strip("\n")
		line = list(map(float,line.split(",")))
		# Pre-processing step where we remove all datapoints with 0 DHI and DNI
		if(line[10] == 0 and line[9] == 0):
			removed_data.append(Entry(line[0],line[1],line[2],line[3],line[12],line[10],line[9],line[7]))
			continue

							#     year    month    day    hour     ghi      dni     dhi   cloud_opac
		day_entry_array.append(Entry(line[0],line[1],line[2],line[3],line[12],line[10],line[9],line[7]))


	day_dhi_values = []
	day_dni_values = []
	day_ghi_values = []
	day_cloud_opacity_values = []
	final_day = 0
	for entry in day_entry_array:
		day_dhi_values.append(entry.dhi)
		day_dni_values.append(entry.dni)
		day_ghi_values.append(entry.ghi)
		day_cloud_opacity_values.append(entry.cloud_opacity)

	day_dhi_average = sum(day_dhi_values)/len(day_dhi_values)
	day_dni_average = sum(day_dni_values)/len(day_dni_values)
	day_ghi_average = sum(day_ghi_values)/len(day_ghi_values)
	day_cloud_opacity_average = sum(day_cloud_opacity_values)/len(day_cloud_opacity_values)
			   #     year    month    day    ghi      dni     dhi   cloud_opac
	final_day = Day(line[0],line[1],line[2],day_ghi_average,day_dni_average,day_dhi_average,day_cloud_opacity_average,index)
# 	^ contains the average data for the last 24 hours

	# copy day array
	original_copy = copy.deepcopy(day_array)

	# KNN part
	for day in day_array:
		day.distance = math.sqrt((day.dni-final_day.dni)**2+(day.dhi-final_day.dhi)**2+(day.cloud_opacity-final_day.cloud_opacity)**2)

	# sort day array according to distance. Will be sorted in ascending order
	day_array.sort(key=lambda x: x.distance)
	closest_day = day_array[0]
	# we can then get the first element in the sorted list as this will have the lowest distance value



	counter = 0
	day_found = 0
	# look for the entry with the index AFTER the closest day. after the first datapoint is found write the headers to the output file
	# then simply write the next 72 lines (meaning the next 72 hours) into the output file as the weather forecast
	for entry in complete_entry_array:
		if(entry.year == original_copy[closest_day.index+1].year and entry.month == original_copy[closest_day.index+1].month and entry.day == original_copy[closest_day.index+1].day and day_found == 0):
			output_file.write(header1+"\n")
			output_file.write(header2+"\n")
			day_found += 1
			counter+=1
		if day_found == 1:
			entry_string = str(list(entry)[3:])
			entry_string = entry_string.strip("[")
			entry_string = entry_string.strip("]")
			output_file.write(entry_string+"\n")
			counter+=1
		if counter > 72:
			break

				

	#####################################     END OF TESTING     #####################################
	training_file.close()
	output_file.close()
	
main()