import json
import os.path
import datetime
from pymongo import MongoClient
from collections import OrderedDict

currentDT = datetime.datetime.now() 
time = currentDT.strftime("%Y-%m-%d %H:%M:%S")
file_dir = os.getcwd()
jsr_dir = os.path.dirname(os.path.dirname(file_dir))

client = MongoClient()
db = client.solverstatistics
collection = db.stats_collection

with open('corpus.json') as json_file:
    json_object = json.load(json_file)
    projects = json_object['projects'] 

for project in projects:
 
    os.chdir(jsr_dir + '/corpus/' + project)    
    os.system(projects[project]['clean'])                                  
    os.system(jsr_dir + '/ontology/run-dljc.sh ' 
    + projects[project]['build'])   
    infer_result = OrderedDict()
    infer_result['time'] = time
    infer_result['project'] = project

    with open('solver-statistic.json') as data_file:
        json_data = json.load(data_file)                                                 
        infer_result['metrics'] = json_data
    
    collection.insert_one(infer_result)  
    os.remove('solver-statistic.json')

