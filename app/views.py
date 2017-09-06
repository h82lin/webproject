from app import app
from flask import render_template, request
from pymongo import MongoClient
import pygal
from pygal.style import Style
import numpy as np
from datetime import datetime, timedelta

client = MongoClient()                       #Use MongoClient() to connect to the running mongo instance                   
db = client.solverstatistics                 #Connect to database named "solverstatistics", create one if such database doesn't exist
collection = db.stats_collection             #Connect to collection named stats_collection in solverstatistics database, create such collection if it doesn't already exist

@app.route('/' , methods=['GET', 'POST'])
def home_page():
    projects = collection.distinct('project')            #Obtain all projects in database
    projects.insert(0,'All')
    docs = collection.find()
    metrics = []
    metrics.append('All')
    for d in docs:
        for key in d['metrics']:
            if(key not in metrics):
                metrics.append(key)                      #Obtain all metrics in database
    
    return render_template('base.html', projects=projects, metrics=metrics)


@app.route('/graphs', methods=['GET', 'POST'])
def graphs():
    dateFrom = request.form['begin']                     #Obtain user-input of starting date from base.html
    dateTo = request.form['end']                         #Obtain user-input of end date from base.html
    good = type(dateTo)
    renderby = request.form['renderby']                  #Obtain user-input on whether to render by projects or metrics
    chart_list = []
    pinput = request.form.getlist('projects')            #Obtain user selection of which projects to display  
    minput = request.form.getlist('metrics')             #Obtain user selection of which metrics to display
    checkp = ''.join(pinput)
    checkm = ''.join(minput)
    custom_style = Style(title_font_size=30, transition = False, value_font_size=10)    #Styling for the pygal graph                                       
    
    if (renderby == 'projects'):                         #If user has chosen to render by projects
        if (checkp != 'All'):
            projects = pinput                            #projects stores a list of user selected project names
        else:
            projects = collection.distinct('project',{'time':{'$gte':dateFrom, '$lte':dateTo}})            #Querying mongo database for all project names within user-input time range

        if (checkm != 'All'):
            metrics = minput                             #metrics stores a list of user selected metric names

        for project in projects:
                                       
            line_chart = pygal.DateTimeLine(print_labels=True, tooltip_fancy_mode= False, x_label_rotation=25, width=800, height=500, legend_box_size=10, max_scale=5, style=custom_style, x_value_formatter=lambda dt: dt.strftime('%b-%d-%Y %I:%M:%S %p'), show_x_guides=True)                             #Creating a pygal DatetimeLine graph
        
            docs = list(collection.find({'time':{'$gte':dateFrom, '$lte':dateTo}, 'project': project}))           #Querying mongo database to find a list of documents within a certain datetime range and containing specific projects
         
            if (checkm == 'All'):
                metrics = []
                for doc in docs:
                    for key in doc['metrics']:
                        if(key not in metrics):
                            metrics.append(key)                                   #Store all metrics under specific projects under 'metric'
    
            for metric in metrics:
                values = []
                for doc in docs:
                    for key in doc['metrics']:
                        if(key == metric):
 			    time = datetime.strptime(doc['time'], '%Y-%m-%d %H:%M:%S')                               #Reformat the time to a datetime object
                            time = time - timedelta(hours=5)                                                         #Pygal library uses UTC time for its datetime graphs, minus 5 hours(EST) to obtain the correct UTC representation
                            values.append({'label': str(doc['metrics'][key]), 'value':(time,doc['metrics'][key])})   #Append the value under a metric with its corresponding time to variable 'values'
                    
                line_chart.add(metric, values)                     #Add all values and time with a metric name to the linechart
            line_chart.title = project
            chart = line_chart.render_data_uri()                   #Store the uri of the generated graph
            chart_list.append(chart)


    elif (renderby == 'metrics'):                                   #If user has chosen to render by metrics
        if (checkm != 'All'):
            metrics = minput

        else:
            docs = collection.find({'time':{'$gte':dateFrom, '$lte':dateTo}})
            metrics = []
            for d in docs:
                for key in d['metrics']:
                    if(key not in metrics):
                        metrics.append(key)
        if (checkp != 'All'):
            projects = pinput

        for metric in metrics:                                          
            line_chart = pygal.DateTimeLine(print_labels=True, tooltip_fancy_mode= False, x_label_rotation=35, width=800, height=500, legend_box_size=10, max_scale=5, style=custom_style, x_value_formatter=lambda dt: dt.strftime('%b-%d-%Y %I:%M:%S %p'), show_x_guides=True)
        
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
                        time = time - timedelta(hours=5)
                        values.append({'label': str(doc['metrics'][metric]), 'value':(time,doc['metrics'][metric])})

                line_chart.add(project, values)
            line_chart.title = metric
            chart = line_chart.render_data_uri()
            chart_list.append(chart)
        

    if(len(chart_list) % 2 != 0):                                      #If the amount of charts to be rendered is an odd number, append a 'None' to the end of the chart_list to tell the html side to not display a graph since the html side only displays 2 graphs per row each time.
            chart_list.append(None)
    chart_list = np.array(chart_list)
    charts = np.reshape(chart_list, (-1, 2))                            #Resize the chart_list to a 2D list to display 2 graphs per row on the html side
    return render_template('graphs.html', charts=charts, good=good)                #Render graphs.html and return the newly generated graphs
