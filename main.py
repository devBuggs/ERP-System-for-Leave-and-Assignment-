from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3, os
import re
import random

app =Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection of the application)
app.secret_key = os.urandom(24)

@app.route("/")
def main():
    return render_template('index.html')

# Leave module routing functions
@app.route("/home/leave-Approved")
def leaveApproved():
    '''
    status = 'approved'
    if request.method == 'POST':
        db = sqlite3.connect("project.sqlite3")
        #getcursor object it is responsible for handling database query
        cursor = db.cursor()
        #Execute database query
        cursor.execute('SELECT * FROM leaveApproved WHERE status = ?', (status))
        # Fetch one record and return result
        account = cursor.fetchall()

        db.close()
    '''
    return ("<h1>Leave Approved Fragment!</h1>")

@app.route("/home/leave-Pending")
def leavePending():
    return ("<div><h1>Leave Pending Fragment!</h1></div")

@app.route("/home/leave-Rejected")
def leaveRejected():
    return ("<h1>Leave Rejected Fragment!</h1>")

@app.route("/leaveApply")
def leaveApply():
    return render_template('leaveApply.html')

# Assignment module routing functions
@app.route("/home/assignment-Create")
def assignmentCreate():
    #return ("<h1>Assignment Creation Wizard!</h1>")
    return render_template('createAssignment.html')

@app.route("/home/assignment-Update")
def assignmentUpdate():
    #return ("<h1>Assignment Updation Wixzard!</h1>")
    return render_template('updateAssignment.html')

@app.route("/home/assignment-Delete")
def assignmentDelete():
    #return ("<h1>Assignment Deletion Wizard!</h1>")
    return render_template('deleteAssignment.html')

# Student Report module routing functions
@app.route("/home/students")
def allStudents():
    return ("<h1>All Students Data</h1>")

@app.route("/home/report-Update")
def reportUpdate():
    return ("<h1>Student Report Updation Module!</h1>")

@app.route("/home/report-Download")
def reportDownload():
    return ("<h1>Student Report Download Module!</h1>")

@app.route("/home/report-Reset")
def reportReset():
    return ("<h1>Student Report Reset Module!</h1>")

# http://localhost/login/ - this will be the login page, we need to use both GET and POST requests
@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msgError = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # opening database sqlite3
        db = sqlite3.connect("project.sqlite3")
        #getcursor object it is responsible for handling database query
        cursor = db.cursor()

        #Execute database query
        cursor.execute('SELECT * FROM userinfo WHERE username = ? AND password = ?', (username, password,))
        
        ####cursor.execute('SELECT * FROM userinfo INNER JOIN studentinfo ON studentinfo.student_id=userinfo.student_id where username=? AND password=?', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        db.close()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            #session['id'] = account['userid']
            session['id'] = account[0]
            session['username'] = account[1]

            #checking usertype
            if account[4] == "faculty":
                return ("<h1>Faculty Dashboard</h1>")

            elif account[4] == "student":
                return("<h1>Student dashboard</h1>")
            # Redirect to home page
            # return 'Logged in successfully!'
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msgError = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msgError)

# http://localhost/login/logout - this will be the logout page
@app.route('/login/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost/login/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/login/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        usertype = request.form['accesstype'] 
        # Check if account exists using MySQL
        db = sqlite3.connect("project.sqlite3")
        cursor = db.cursor()
        #cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        cursor.execute('SELECT * FROM users WHERE username = ?', (request.form['username'],))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            userid = random.randrange(999999)
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?)', (userid,username, password, email, usertype))
            db.commit()
            db.close()
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost/login/home - this will be the home page, only accessible for logged-in users
@app.route('/login/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost/login/profile - this will be the profile page, only accessible for logged-in users
@app.route('/login/profile', methods = ['POST', 'GET'])
def profile():
    account = []
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        db = sqlite3.connect("project.sqlite3")
        #getcursor object it is responsible for handling database query
        cursor = db.cursor()
        #Execute database query
        cursor.execute('SELECT * FROM users WHERE userid = ?', (session['id'],))
        
        account = cursor.fetchone()
        db.commit()
        
        #close the database connection
        db.close()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(debug=True, host="0.0.0.0", port=80)
