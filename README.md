# Flask-Application

CPSC 449 - Midterm Project

Team Members:
Meghana Bodapati Thirumalanaidu - meghanabt@csu.fullerton.edu (CWID - 885206029)
Pooja Honneshwari Ravi - pooja.ravi@csu.fullerton.edu (CWID - 885237305)
Shriya Bannikop - shriyabannikop@csu.fullerton.edu (CWID - 885196238)

Steps to install and configure Flask:

-> First create a folder named flask project and change directory to it. If you are on linux then type the following in your terminal.

        mkdir "flask project" && cd "flask project"
        
-> Now, create a virtual environment. If you are on linux then type the following in your terminal.
                python3 -m venv env
This will create a folder named venv in the flask project which will contain the project specific libraries. 

-> Now create a file named requirements.txt and add the following lines in it.
                Flask-RESTful==0.3.8
                PyJWT==1.7.1
To install these libraries for this project. To do so, first we need to activate the virtual environment. To do so, type the following in your terminal.
source env/bin/activate
Note: If you are on windows then it would be Scripts instead of bin

-> Now, it's time to install the libraries. To do so, again type the following in your terminal. 
            pip install -r requirements.txt
Now, we are done with the setup part. 

-> Create a python file called app.py and import necessary packages to setup app.

Steps  to install and setup Mysql:
Install ‘mysqldb’ module in the set virtual environment.
Flask-MySQLdb provides MySQL connection for Flask, for that run the below command.

$ pip install flask-mysqldb
Now add the below code to connect mysql with flask application
from flask import Flask
from flask_mysqldb import MySQL
conn = pymysql.connect(
        host='localhost',
        user='root', 
        password = "",
        db='449_db',
        )
        
-> To run the project run the following command:
		flask run
Now your project will be running in the following url: http://localhost:5000
