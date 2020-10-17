from timeit import default_timer as dt
import numpy as np
from multiprocessing import Process,Array,Value
from threading import Thread

cores = 18
nodes = 16
gsize = 0.5
node = 0

st = dt()
veckey = list(QgsProject.instance().mapLayers().keys())[1]
vectorlayer = QgsProject.instance().mapLayers()[veckey]
key = list(QgsProject.instance().mapLayers().keys())[0]
grid = QgsProject.instance().mapLayers()[key]

count = 0

def counter(feats,vectors,arr,i):
    cnt = 0
    for feature in feats:
        cands = vectors.getFeatures(QgsFeatureRequest().setFilterRect(feature.geometry().boundingBox()))
        for area_feature in cands:
            if feature.geometry().intersects(area_feature.geometry()):
                cnt+=1
    print(cnt)
    arr[i] = cnt
    
gfeats = np.array(list(grid.getFeatures()))
print(len(gfeats))
gsubs = np.array_split(gfeats,nodes)
print(len(gsubs[node]))
subs = np.array_split(gsubs[node],cores)

threads = []
arr = Array('i',range(cores))

i=0
for sub in subs:
    proc = Process(target=counter,args=(sub,vectorlayer.clone(),arr,i))
    threads.append(proc)
    proc.start()
    i+=1

for proc in threads:
    proc.join()
    

sum = 0
for x in arr:
    sum+=x

ctime = dt()-st

f = open("//home//jaideep.gedi.17cse//qgis//india.txt","a+")
f.write("grid size : "+str(gsize)+"\n")
f.write("node : "+str(node)+"\n")
f.write("count : "+str(sum)+"\n")
f.write("time : "+str(ctime)+"\n\n")
f.close()

print(sum)
print(ctime)
