import json
import pygal
from pygal.style import Style
from pymongo import MongoClient
import datetime

currentDT = datetime.datetime.now() 
currTime = currentDT.strftime('%Y-%m-%d %H:%M:%S')

client = MongoClient()                  
db = client.solverstatistics                
collection = db.stats_collection 

def validate_date(d):
    try:
        datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
        return True
    except:
        return False

while(True):
    allTime = raw_input('Display information from all times? (y/n): ')
    if(allTime == 'y' or allTime =='n'):
        break
    else:
        print('Invalid input format')
 
from datetime import datetime

if(allTime =='y'):
    dateFrom = '0000/00/00 00:00:00'
    dateTo = currTime

if(allTime == 'n'):
    while(True):
        try:
            while(True):
                dateFrom = raw_input('Enter starting datetime (YYYY-MM-DD HH:MM:SS): ')
                if(validate_date(dateFrom) == True):
                    break
                else:
	            print('Invalid input format')
                    
            while(True):
                dateTo = raw_input('Enter ending datetime (YYYY-MM-DD HH:MM:SS)/"now" for current datetime: ')
                if(dateTo == 'now'):
                    dateTo = currTime
                if(validate_date(dateTo) == True):
                    break
                else:
	            print('Invalid input format')
        
            search = collection.find({'time':{'$gte': dateFrom, '$lte': dateTo}})                             #Search if there exists data in given time range

            if (search == None):
                raise Exception
            else: 
                break

        except:
            print('No data in given time range')      

while(True):
    renderby = raw_input('Display information by metrics or projects? (metrics/projects): ')
    if(renderby == 'metrics' or renderby =='projects'):
        break
    else:
        print('Invalid input format')

while(True):
    projects = raw_input('Insert projects to display, "All" for all projects (Seperate each projects with space): ')
    projects_list = projects.split()
    checkp = ''.join(projects_list)
    i=0
    if(checkp != 'All'):
        for project in projects_list:
            search = collection.find_one({'project':project})                                                      #Check if user inputted projects exist in database
            if(search == None):
                i=1
                print('\'' + project + '\'' +' does not exist in database')
    if(i==0):
        break 

while(True):
    metrics = raw_input('Insert metrics to display, "All" for all metrics (Seperate each metrics with space): ')
    metrics_list = metrics.split()
    checkm = ''.join(metrics_list)
    i=0
    if(checkm != 'All'):
        for metric in metrics_list:
            search = collection.find_one({'metrics.'+ metric:{'$exists': 'true'}})
            if(search == None):
                i=1
                print('\'' + metric + '\'' +' does not exist in database')
    if(i==0):
        break 

#Above is the logic for user inputs
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#below is the logic for graph generation(Logic is the same as app/views.py)

custom_style = Style(title_font_size=30, transition = False, value_font_size=10)
if (renderby == 'projects'):
    if (checkp != 'All'):  
        projects = projects_list
    else:
        projects = collection.distinct('project',{'time':{'$gte':dateFrom, '$lte':dateTo}})

    if (checkm != 'All'):
        metrics = metrics_list

    for project in projects:                       
        line_chart = pygal.DateTimeLine(print_labels=True, tooltip_fancy_mode= False, x_label_rotation=35, width=800, height=500, legend_box_size=10, max_scale=5, style=custom_style, x_value_formatter=lambda dt: dt.strftime('%b/%d/%Y at %H:%M:%S'), show_x_guides=True)
        
        docs = list(collection.find({'time':{'$gte':dateFrom, '$lte':dateTo}, 'project': project}))
        times = collection.distinct('time',{'time':{'$gte':dateFrom, '$lte':dateTo},'project': project})
         
        if (checkm == 'All'):
            metrics = [] 
            for doc in docs:
                for key in doc['metrics']:
                    if(key not in metrics):
                        metrics.append(key)

        for metric in metrics:
            values = []
            for doc in docs:
                for key in doc['metrics']:
                    if(key == metric):
 		        time = datetime.strptime(doc['time'], '%Y-%m-%d %H:%M:%S')
                        values.append((time,doc['metrics'][key]))
                    
            line_chart.add(metric, values)
        line_chart.title = project
        line_chart.render_to_png('graphs/' + project + '.png')              #Render each graph to seperate png files in the /app folder


elif (renderby == 'metrics'):  
    if (checkm != 'All'):
        metrics = metrics_list

    else:
        docs = collection.find({'time':{'$gte':dateFrom, '$lte':dateTo}})
        metrics = []
        for d in docs:
            for key in d['metrics']:
                if(key not in metrics):
                    metrics.append(key)
    if (checkp != 'All'):
        projects = projects_list

    for metric in metrics:

                                          
        line_chart = pygal.DateTimeLine(print_labels=True, tooltip_fancy_mode= False, x_label_rotation=35, width=800, height=500, legend_box_size=10, max_scale=5, style=custom_style, x_value_formatter=lambda dt: dt.strftime('%b/%d/%Y at %H:%M:%S'), show_x_guides=True)
        
        docs = list(collection.find({'time':{'$gte':dateFrom, '$lte':dateTo}, 'metrics.'+ metric:{'$exists': 'true'}}))
    
            
        if (checkp == 'All'):
            projects = []
            for doc in docs:
                if(doc['project'] not in projects):
                    projects.append(doc['project'])

        for project in projects:
            values = []  
            for doc in docs:
                if(doc['project'] == project):  
                    time = datetime.strptime(doc['time'], '%Y-%m-%d %H:%M:%S')
                    values.append((time,doc['metrics'][metric]))
                    

            line_chart.add(project, values) 
        line_chart.title = metric
        line_chart.render_to_png('graphs/' + metric + '.png')                #Render each graph to seperate png files in the /app folder
    
