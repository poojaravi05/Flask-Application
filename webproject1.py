from flask import Flask, jsonify, request, make_response, render_template, redirect, url_for, send_from_directory, session
import jwt
import datetime
from datetime import timedelta
from functools import wraps
import urllib.request
import os
from werkzeug.utils import secure_filename
import pymysql
from flask_cors import CORS
import re

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SECRET_KEY'] = 'secretkey'
app.permanent_session_lifetime = timedelta(minutes=10)

conn = pymysql.connect(
        host='localhost',
        user='root', 
        password = "",
        db='449_db',
		cursorclass=pymysql.cursors.DictCursor
        )
cur = conn.cursor()

#file validation for file type and file size limit
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True
)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#user model with username and password fields
class user:
    def __init__(self, username, password):
        self.username = username
        self.password = password

#list of users
users = [
    user('Pooja', 'password'),
    user('Ravi', 'password')
]

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token') #https://127.0.0.1:5000/route?token=afhftdchbiuig

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401
        
        try:
            data = jwt.encode().decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message' : 'Token is invalid !!'}), 401
        
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    if not session.get('loggedin'):
        return render_template('homepage.html')
    else:
        return 'logged in currently'

#login endpoint that authenticates the user and returns a JWT token
@app.route('/login')
def login():
    auth = request.authorization

    if auth and auth.password == 'password':
        token = jwt.encode({'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=10)}, app.config['SECRET_KEY'])
        session['loggedin'] = True
        return jsonify({'token' : token.encode().decode('UTF-8')})
    
    return make_response('User not found!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required" '})

#only admin can add users
@app.route("/admin", methods =['GET', 'POST'])
@token_required
def admin():
		if session['username'] == "Pooja" or session['username'] == "Ravi"  :
			return redirect(url_for('register'))
		else:
			return jsonify({'message' : 'User not authorised'}), 401	

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'address' in request.form and 'city' in request.form and 'country' in request.form and 'postalcode' in request.form and 'organisation' in request.form:
		print('reached')
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		organisation = request.form['organisation']
		address = request.form['address']
		city = request.form['city']
		state = request.form['state']
		country = request.form['country']
		postalcode = request.form['postalcode']
		cur.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
		account = cur.fetchone()
		print(account)
		conn.commit()
		if account:
			return make_response('Account already exists !', 202)
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'name must contain only characters and numbers !'
		else:
			cur.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s, % s, % s, % s, % s, % s)', (username, password, email, organisation, address, city, state, country, postalcode, ))
			conn.commit()

			return make_response('Successfully registered.', 201)
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)


@app.route('/unprotected')
def unprotected():
    return jsonify({'message' : 'Token is verified. You can now access all protected informations.!'})

#protected endpoint that requires a valid JWT token to access
@app.route('/protected')
@token_required
def protected():
    return jsonify({'message' : 'This is only available if you have a valid token.'})

#an endpoint that allows users to upload files
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            Flask.flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            Flask.flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            basedir = os.path.abspath(os.path.dirname(__file__))
            file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    elif not session.get('loggedin'):
        return jsonify({'message' : 'User is not authenticated to access this route!'}), 401
    return render_template("upload.html")



@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

#public route that allows users to view public information
@app.route('/public_info')
def public_info():
    public_info = {
        'title': 'Welcome',
        'description': 'This is a public page for everyone to see',
        'contact_email': 'someone@gmail.com'
    }
    info_json = jsonify(public_info)

    return info_json

#an endpoint that returns a list of items that can be viewed publicly
@app.route('/public_items')
def get_public_items():
    items = [
        {'name': 'public_info', 'description': 'Information about the site'},
        {'name': 'Homepage', 'description': 'First page aka Homepage'},
        {'name': 'Unprotected', 'description': 'Unprotected route'},
        {'name': 'Public Items', 'description': 'List of all the routes that can be viewed without authentication'}
    ]
    return jsonify(items)

#error handlers
@app.route('/error')
def raise_error():
    # Raise a custom error with a 400 status code and a message
    raise ValueError('This is a custom error')

# Define an error handler for 400 errors
@app.errorhandler(400)
def bad_request_error(error):
    # Return a JSON response with an error message and status code
    return jsonify({
        'error': 'Bad request',
        'message': error.description
    }), 400

@app.errorhandler(405)
def bad_request_error(error):
    # Return a JSON response with an error message and status code
    return jsonify({
        'error': 'Method not allowed',
        'message': error.description
    }), 405

# Define an error handler for 500 errors
@app.errorhandler(500)
def internal_server_error(error):
    # Return a JSON response with an error message and status code
    return jsonify({
        'error': 'Internal server error',
        'message': error.description
    }), 500

# Define an error handler for 500 errors
@app.errorhandler(401)
def unauthorised_access(error):
    # Return a JSON response with an error message and status code
    return jsonify({
        'error': 'Unauthorised Access',
        'message': error.description
    }), 401

# Define an error handler for 500 errors
@app.errorhandler(404)
def not_found(error):
    # Return a JSON response with an error message and status code
    return jsonify({
        'error': 'Not found',
        'message': error.description
    }), 404


if __name__ == '__main__':
    app.run(debug=True)