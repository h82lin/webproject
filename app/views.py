from app import app
from flask import render_template, request
import numpy as np
from pymongo import MongoClient
import pygal
from pygal.style import Style
#from bashinput import allTime, dateFrom, dateTo, display, allProjects, allMetrics, metrics_list, projects_list

client = MongoClient()
db = client.solverstatistics
collection = db.stats_collection
projects = []
metrics = []

@app.route('/' , methods=['GET', 'POST'])
def home_page():
    return render_template('base.html')


@app.route('/displays',  methods=['GET', 'POST'])
def displays():
    global dateFrom
    global dateTo 
    global renderby
    global projects
    dateFrom = request.form['begin']
    dateTo = request.form['end']
    renderby = request.form['renderby']
    if (renderby == 'projects'):
 
        projects = collection.distinct('project',{'time':{'$gte':dateFrom, '$lte':dateTo}})
        return render_template('displays.html',
                               elements=projects)

    elif(renderby == 'metrics'):
        global metrics
        doc = collection.find({'time':{'$gte':dateFrom, '$lte':dateTo}})
        for d in doc:
            for key in d['metrics']:
                if(key not in metrics):
                    metrics.append(key)
        return render_template('displays.html',
                                elements=metrics)


@app.route('/graphs', methods=['GET', 'POST'])
def graphs():
    chart_list = []
    display = request.form.getlist('display')
    check = ''.join(display)
    custom_style = Style(title_font_size=30, transition = False, value_font_family='googlefont:Raleway', value_font_size=10, value_colors=('black'))                                           
    global projects


    if (renderby == 'projects'):
        if (check != 'all'):  
            projects = display

        for project in projects:
            metric_store = []                             
            line_chart = pygal.Line(print_values=True, print_values_position='top', tooltip_fancy_mode= False, x_label_rotation=35, width=800, height=500, logarithmic=False, legend_box_size=10, max_scale=3, style=custom_style, x_value_formatter=lambda dt: dt.strftime('%Y/%m/%d at %H:%M:%S'))
        
            docs = list(collection.find({'time':{'$gte':dateFrom, '$lte':dateTo}, 'project': project}))
            times = collection.distinct('time',{'time':{'$gte':dateFrom, '$lte':dateTo}, 'project': project})
           
            for doc in docs:
                for key in doc['metrics']:
                    if(key not in metric_store):
                        metric_store.append(key)

            for metric in metric_store:
                value_store = []
                time_store = []
		i = 0
                for doc in docs:
                    for key in doc['metrics']:
                        if(key == metric):
                            value_store.append(doc['metrics'][key])
                            time_store.append(doc['time'])
                  
                diff = list(set(times) - set(time_store))
		for d in diff:
                    value_store.insert(times.index(d), None)
                    
                line_chart.add(metric, value_store)
            line_chart.x_labels = (times)    
            line_chart.title = project
            chart = line_chart.render_data_uri()
            chart_list.append(chart)       


    elif (renderby == 'metrics'):
        global metrics
        if (check != 'all'):
            metrics = display

        for metric in metrics:
            project_store = []
                                          
            line_chart = pygal.Line(print_values=True, print_values_position='top', x_label_rotation=35, y_labels_major_every=3, width=700, height=437, logarithmic=False, legend_box_size=10, max_scale=3, style=custom_style)
        
            docs = list(collection.find({'time':{'$gte':dateFrom, '$lte':dateTo}, 'metrics.'+ metric:{'$exists': 'true'}}))
	    times = collection.distinct('time',{'time':{'$gte':dateFrom, '$lte':dateTo}, 'metrics.'+ metric:{'$exists': 'true'}})
            for doc in docs:
                if(doc['project'] not in project_store):
                    project_store.append(doc['project'])

            for project in project_store:
                value_store = []  
                time_store = []   
                for doc in docs:
                    if(doc['project'] == project):  
                        value_store.append(doc['metrics'][metric])
                        time_store.append(doc['time'])
             
                diff = list(set(times) - set(time_store))
		for d in diff:
                    value_store.insert(times.index(d), None)

                line_chart.add(project, value_store) 
                line_chart.x_labels = (times)
            line_chart.title = metric
            chart = line_chart.render_data_uri()
            chart_list.append(chart)
        

    if(len(chart_list) % 2 != 0):
            chart_list.append(None)
    chart_list = np.array(chart_list)
    charts = np.reshape(chart_list, (-1, 2))
    return render_template('graphs.html', charts=charts)
