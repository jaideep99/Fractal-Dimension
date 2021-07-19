# This PROGRAM calculates the fractal dimension of the coastline and border of India using the box counting method.
#
# The features/boxes of grid are distributed between the nodes and each node distributes features between its cores.
# At each core, the function : counter() is executed and results are stored in a Multiprocessing array and summated to get the count of boxes.
#
# The maps and shapefiles are taken from GADM (https://gadm.org/download_country_v3.html)
#
# Authors: Jaideep Reddy, Deepika Bisht (BML Munjal University Gurgaon, India)
#
# Last Modified:18-07-2021


#importing multiprocessing libraries
from timeit import default_timer as dt
import numpy as np
from multiprocessing import Process,Array,Value

#provide the following
cores = 18      # no of cores
nodes = 4       # no of nodes
gsize = 0.5     # grid size
node = 0        # node number


st = dt()
veckey = list(QgsProject.instance().mapLayers().keys())[1]      # Get the key for map/india layer
instancelayer = QgsProject.instance().mapLayers()[veckey]       # Use key to get the map/india layer
key = list(QgsProject.instance().mapLayers().keys())[0]         # Get the key for grid layer
grid = QgsProject.instance().mapLayers()[key]                   # Use grid key to get the grid layer

# This function : counter() returns the count of boxes that contains a part of coastline / intersects with coastline.
def counter(gridfts,instvectors,arr,i):
    cnt = 0
    for feature in gridfts:
        # Get the features of map within boundary of grid feature
        areas = instvectors.getFeatures(QgsFeatureRequest().setFilterRect(feature.geometry().boundingBox()))
        for area_feature in areas:
            if feature.geometry().intersects(area_feature.geometry()):          # if a map feature intersects with the grid feature count +1 
                cnt+=1
    arr[i] = cnt            # Store the count of intersections into Multiprocessing Array


gfeats = np.array(list(grid.getFeatures()))         # Get the list of grid layer features
gsubs = np.array_split(gfeats,nodes)                # Split the features list between the nodes 
subs = np.array_split(gsubs[node],cores)            # Take the features of current node and split them into no of cores

procs_list = []
arr = Array('i',range(cores))                       # Create an Multiprocessing array to store results from each core

i=0
for sub in subs:
    proc = Process(target=counter,args=(sub,instancelayer.clone(),arr,i))   # Create process to count the intersections
    procs_list.append(proc)                                                 # Add process to the procs_list
    proc.start()                                                            # Start process
    i+=1

for proc in threads:
    proc.join()                                                             # Wait till all processes ends (join)
    

count = 0               # count of intersections
for x in arr:
    count+=x            # Sum all intersection counts from all cores    

ctime = dt()-st

# Write the results
f = open("//home//qgis//indiaresults.txt","a+")
f.write("grid size : "+str(gsize)+"\n")
f.write("node : "+str(node)+"\n")
f.write("count : "+str(count)+"\n")
f.write("time : "+str(ctime)+"\n\n")
f.close()
