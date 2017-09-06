## User manual:
* The website uses the flask web-framework. If you have any problems on how to operate with flask, this tutorial will give you some insight: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world.
* To start the website, simply execute the run.py script in the main directory.

* The __/app/views.py__ file contains all the backend for the website.
* The __/app/datastore.py__ file cleans and runs dolikejavac on each project listed in the corpus.json file. It then store the     results into a database.
* The __/app/reset.py__ file when run, deletes all data in the mongodb collection.
* The __/app/\_\_init\_\_.py__ file creates the application object of class Flask and imports the views module (needed for the flask  web-framework).
* The __/app/bashinput.py__ file is a bash script designed to obtain user inputs, it then outputs analytical graphs in png format at the /app/graphs directory. It has the same functionality as the website.
* The __/app/templates__ directory contains all the html files needed for the front-end of the website. __base.html__ is the homepage of the website. __graphs.html__ is the page that displays all the analytical graphs.

## Dependencies:
* The scripts in this repository use the pygal python library to generate analytical graphs. <br />
For the full pygal documentation: http://pygal.org/en/stable/index.html <br />
Install pygal by:<br />
```
pip install pygal
```

* When using the /app/bashinput.py file to generate graphs in png format, if the png file ends up turning black; installing lxml, tinycss and cssselect should fix the issue.

* The graph generation scripts in this repository uses mongodb as its database. Please install mongodb with instructions in: https://docs.mongodb.com/manual/administration/install-community/.

* The scripts in this repository uses pymongo to communicate with mongodb. Make sure pymongo is installed. <br />
Install pymongo by: <br />
```
python -m pip install pymongo
```

