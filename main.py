from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3, os
import re
import random
from datetime import date 

app =Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection of the application)
app.secret_key = os.urandom(24)

@app.route("/")
def main():
    return render_template('index.html')

# faculty handle
@app.route("/home/leave-Approve")
def leaveApprove():
    return ("<h1>Leave Approved Fragment!</h1>")

# faculty handle
@app.route("/home/leave-Rejected")
def allLeaveStatus():
    return ("<h1>Leave all-Leave-Status Fragment!</h1>")
    
# student request - done
@app.route("/login/leaveApply", methods=['GET', 'POST'])
def leaveApply():
    msg = 'Leave request is successfully submitted'
    if request.method == 'POST' and 'leave_from' in request.form and 'leave_upto' in request.form and 'leave_reason' in request.form:
        if 'loggedin' in session:
            # Create variables for easy access
            leaveFrom = request.form['leave_from']
            leaveUpto = request.form['leave_upto']
            leaveReason = request.form['leave_reason']
            approve = 0
            pending = 1
            userName = session['username']
            # opening database sqlite3
            db = sqlite3.connect("project.sqlite3")
            #get cursor object it is responsible for handling database query
            cursor = db.cursor()
            # checking the student_id via sql Query
            cursor.execute('SELECT student_id FROM userinfo WHERE username = ?', (userName,))
            studentID = cursor.fetchone()
            sID = studentID[0]
            print(sID)
            #Execute database query
            cursor.execute('INSERT INTO leaveinfo(leave_from, leave_upto, reason, student_id, is_approve, is_pending) VALUES(?,?,?,?,?,?)', (leaveFrom, leaveUpto, leaveReason, sID, approve, pending),)
            print("leave apply is register and Database is commited.........")
            db.commit()
            db.close()
            print(cursor.lastrowid)
            print('Yeeeepppppppppppppppppppeeeeeeeeeee')
            return render_template('leaveApply.html', msg = msg)
        #corrently working.......
        return redirect(url_for('login'))
    return render_template('leaveApply.html')

# student leave status - done
@app.route("/leaveStatus")
def leaveStatus():
    data=[]
    if 'loggedin' in session:
        user = session['id']
        # We need all the leave info. for the user so we can display it on the view assignment page
        db = sqlite3.connect("project.sqlite3")
        cursor = db.cursor()
        cursor.execute('SELECT leaveinfo.* FROM leaveinfo INNER JOIN userinfo ON userinfo.student_id = leaveinfo.student_id where userinfo.user_id=?',(user,))
        data = cursor.fetchall()
        print(data) #for testing purpose.. in CONSOLEs
        db.close()
        #if data != None:
            #return render_template('leaveStatus.html', data=data)
        return render_template('leaveStatus.html', data=data)
    return redirect(url_for('login'))

# faculty handle assignment - working
@app.route("/home/assignment-Create")
def assignmentCreate():
    if request.method == 'POST' and 'assignmentName' in request.form and 'submissionDate' in request.form and 'class' in request.form and 'note' in request.form and 'file' in request.form:
        # Create variables for easy access
        name = request.form['assignmentName']
        dos = request.form['submissionDate']
        classData = request.form['class']
        note = request.form['note']
        fileData = request.form['file']
        upload_date = date.today()
        # opening database sqlite3
        db = sqlite3.connect("project.sqlite3")
        #get cursor object it is responsible for handling database query
        cursor = db.cursor()
        #Execute database query
        cursor.execute('INSERT INTO assignmentinfo(name, file, dos, upload_date, class, instruction, faculty_id) VALUES(?,?,?,?,?,?,?)', (name, fileData, dos, upload_date, classData, note, session['id']),)
        db.commit()
        db.close()
        print(cursor.lastrowid, "INSERTED DATA at ASSIGNMENT TABLE")
        return render_template('createAssignment', msg = msg)
        #corrently working.......
    return render_template('createAssignment.html')

# student view - done
@app.route("/viewAssignment")
def viewAssignment():
    data=[]
    if 'loggedin' in session:
        user = session['id']
        #print(user)
        # We need all the assignment info. for the user so we can display it on the view assignment page
        db = sqlite3.connect("project.sqlite3")
        cursor = db.cursor()
        cursor.execute('SELECT assignmentinfo.*, facultyinfo.name, facultyinfo.subject from userinfo inner join studentinfo on studentinfo.student_id = userinfo.student_id inner join assignmentinfo on assignmentinfo.class = studentinfo.class inner join facultyinfo on facultyinfo.class = assignmentinfo.class where userinfo.user_id = ?',(user,))
        data = cursor.fetchall()
        # print(data) #for testing purpose.. in CONSOLEs
        db.close()
        if data == None:
            return render_template('viewAssignment.html', data=data)
    return render_template('viewAssignment.html', data=data)

# student download btn - done (file-picker)
@app.route("/login/downloadFile/<assign_id>", methods=['GET'])
def downloadFile(assign_id):
    print("In downloadFile function")
    if request.method == 'GET':
        # print(assign_id)
        try:
            db = sqlite3.connect("project.sqlite3")
            cursor = db.cursor()
            cursor.execute('SELECT * from assignmentinfo where assignment_id = ?', (assign_id,))
            data = cursor.fetchone()
            file_data = data[1]
            if assign_id == '1':
                file_name = 'download.jpg'
            elif assign_id == '2':
                file_name = 'download.docx'
            elif assign_id == '3':
                file_name = 'download.pdf'
            else:
                file_name = 'download'
            file_path = os.getcwd() + '\\' + file_name
            with open(file_name, 'wb') as file:
                file.write(file_data)
            # full_path = os.path.join(os.getcwd(), 'download.jpg')

        except sqlite3.Error as error:
            print('Failed')

        finally:
            if(db):
                db.close()

    # msg = 'Assignment file downloaded at location C:/Users/Downloads'
    return("<h2>Assignment file downloaded at location "+ file_path +"</h2>")
    # return redirect(url_for('viewAssignment'))

# faculty handle
@app.route("/home/assignment-Update")
def assignmentUpdate():
    return render_template('updateAssignment.html')

# faculty handle - done
@app.route("/home/assignment-Delete")
def assignmentDelete():
    if request.method == 'GET':
        if 'loggedin' in session:
            user = session['id']
            #print(user)
            # We need all the assignment info. for the user so we can display it on the view and delete it
            db = sqlite3.connect("project.sqlite3")
            cursor = db.cursor()
            cursor.execute('SELECT assignmentinfo.name, assignmentinfo.upload_date, assignmentinfo.dos, assignmentinfo.class, assignmentinfo.instruction, assignmentinfo.assignment_id FROM userinfo INNER JOIN assignmentinfo ON userinfo.faculty_id = assignmentinfo.faculty_id WHERE user_id=?',(user,))
            data = cursor.fetchall()
            print(data) #for testing purpose.. in CONSOLEs
            db.close()
            if data != None:
                return render_template('deleteAssignment.html', data=data)
        return redirect(url_for('login'))
    return render_template('deleteAssignment.html')

# faculty handle - done
@app.route("/deleteNow/id/<int:objID>', methods=['GET','POST']")
def deleteNow(objID):
    print(objID, 'assignment id receved.')
    if request.method == 'GET':
        if 'loggedin' in session:
            #errorMsg = 'Unable to delete this assignment...'
            msgdata = 'Assignment deleted successfully...'
            # We need all the assignment info. for the user so we can display it on the view and delete it
            db = sqlite3.connect("project.sqlite3")
            cursor = db.cursor()
            cursor.execute('DELETE FROM assignmentinfo WHERE assignment_id =?',(objID,))
            #data = cursor.fetchone()
            db.commit()
            #print(data) #for testing purpose.. in CONSOLE
            db.close()
            print(objID,"no assignment is deleted.")
            msgdata = 'Assignment deleted successfully...'
            return redirect(url_for('assignmentDelete', value=msgdata)) #render_template('deleteAssignment.html', value=msgdata)
        return redirect(url_for('login'))

@app.route("/home/students")
def allStudents():
    return render_template('allStudents.html')

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
    # Check if "email" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # opening database sqlite3
        db = sqlite3.connect("project.sqlite3")
        #get cursor object it is responsible for handling database query
        cursor = db.cursor()
        #Execute database query
        cursor.execute('SELECT * FROM userinfo WHERE email = ? AND password = ?', (email, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        db.close()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]

            #checking usertype
            if account[4] == "faculty":
                render_template('facultyDashboard.html')
            elif account[4] == "student":
                render_template('studentDashboard.html')
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
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'student_id' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        student_id = request.form['student_id']
        usertype = 'student'
        # Check if account exists using MySQL
        db = sqlite3.connect("project.sqlite3")
        cursor = db.cursor()
        # cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        cursor.execute('SELECT * FROM studentinfo WHERE student_id = ?', (request.form['student_id'],))
        id_found = cursor.fetchone()
        cursor.execute('SELECT * FROM userinfo WHERE email = ?', (request.form['email'],))
        email_found = cursor.fetchone()
        cursor.execute('SELECT * FROM userinfo WHERE username = ?', (request.form['username'],))
        user_found = cursor.fetchone()

        # validation checks
        if not id_found:
            msg = 'Invalid Student ID!'
        elif id_found and int(id_found[7]):
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email or not student_id:
            msg = 'Please fill out the form!'
        elif email_found or user_found:
            msg = 'Username/Email already exists!'
        else:
            # userid = random.randrange(999999)
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO userinfo (username, password, email, usertype, student_id) VALUES (?, ?, ?, ?, ?)', (username, password, email, usertype, student_id))
            cursor.execute('update studentinfo set "is_register" = "1" where student_id = ?', (request.form['student_id'],))
            db.commit()
            db.close()
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost/login/home - this will be the home page, only accessible for logged-in users
@app.route('/login/home', methods=['GET', 'POST'])
def home():
    account=[]
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        db = sqlite3.connect("project.sqlite3")
        #getcursor object it is responsible for handling database query
        cursor = db.cursor()
        #Execute database query
        cursor.execute('SELECT * FROM userinfo WHERE user_id = ?', (session['id'],))
        account = cursor.fetchone()
        #close the database connection
        db.close()
        if account[4] == "faculty":
            return render_template('facultyDashboard.html', username=session['username'])
        elif account[4] == "student":
            return render_template('studentDashboard.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost/login/profile - this will be the profile page, only accessible for logged-in users
@app.route('/login/profile', methods=['GET', 'POST'])
def profile():
    account = []
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        db = sqlite3.connect("project.sqlite3")
        #getcursor object it is responsible for handling database query
        cursor = db.cursor()
        #Execute database query
        cursor.execute('SELECT * FROM userinfo WHERE user_id = ?', (session['id'],))
        account = cursor.fetchone()
        db.commit()
        #close the database connection
        db.close()
        if account[4] == "faculty":
            return render_template('profile.html', account=account)
        elif account[4] == "student":
            return render_template('studentProfile.html', account=account)
        #return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(debug=True, host="0.0.0.0", port=80)
