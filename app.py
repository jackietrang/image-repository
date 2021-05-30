import os, re
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user, login_manager
from flask import Flask, render_template, redirect, url_for, request, g, session, flash
from flask_sqlalchemy import SQLAlchemy
import urllib.request
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from utils import * 

#######################################
###### FLASK APP CONFIGURATION ########
#######################################
# set up project directory
project_dir = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))
# Set up flask app configuration
main = Flask(__name__, template_folder='./templates', static_folder='./static')
UPLOAD_FOLDER = './static/uploads/'
main.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
main.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
main.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(main)
# Set up app and Flask-Login for them to work together
main.secret_key = "jackie trang" # required a secret key for session authentication
signin = LoginManager() #built-in class LoginManager()
signin.init_app(main)  # configure app for login
signin.login_view = 'signin'
main.testing = True # allow context for unittest

#######################################
###### DATABASE SCHEMA ################
#######################################
# Intialize Task and User objects
class Image(db.Model):
    '''
    Image has foreign key link to User table
    '''
    __tablename__ = 'Image'
    filename = db.Column(db.String(100), nullable=True, unique=False)
    unique_count = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('User.id'))

class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    image_id = db.relationship('Image', backref='User')

# Creates database for users and tasks
db.create_all()
# Generates entries for the database
db.session.commit()


#######################################
########## APP CONTEXT ################
#######################################
@main.route('/', methods=['GET'])
def default():
    '''
    By default, users are routed to log in page
    '''
    return redirect('signin')

@signin.user_loader
def load_user(id):
    '''
    This sets the callback for reloading a user from the session. 
    The function you set should take a user ID (a unicode)
     and return a user object, or None if the user does not exist.
    '''
    return User.query.get(int(id))

@main.before_request
def before_request():
    '''
    Set g.user to current_user before running any requests
    '''
    g.user = current_user

#######################################
########## USER AUTHORIZATION #########
#######################################
@main.route('/signup', methods=['GET','POST'])
def signup():
    '''
    Sign up new users with password requirements
    - POST request: Save user sign-up information to db and redirect them to log-in page
        + Password must contain both letters and numbers
    - GET request: render sign-up page
    '''
    if request.method == 'POST':
        # Checks password requirements
        password = request.form.get('password')
        # password needs at least 1 number
        if re.search('[0-9]', password) is None:
            error_msg = "Password needs at least one number"
            return render_template("signup.html", error=error_msg)
        # password needs at least 1 letter
        elif re.search('[a-z]', password) is None:
            error_msg = "Password needs at least one letter"
            return render_template("signup.html", error=error_msg)
        # password and re-entered password match
        if password != request.form['repeat']:
            error_msg = "Password doesn't match"
            return render_template("signup.html", error=error_msg)
        username = request.form.get('user_email')
        existed_usernames = {user.username for user in User.query.all()}
        if username in existed_usernames:
            error_msg = "Username already existed. Please choose a new name."
            return render_template("signup.html", error=error_msg)

        # store hashed password to db for security
        signup_user = User(username=username, password=generate_password_hash(password)) # new instance of user
        # add user login + password to db
        db.session.add(signup_user)
        db.session.commit()
        return redirect("/signin")

    elif request.method == 'GET':
        return render_template('signup.html')

@main.route('/signin', methods=['GET', 'POST'])
def signin():
    ''' 
    Log in existing user based on their user email and password.
    '''
    if request.method == 'POST':
        username = request.form.get('user_email')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first() #query user
        # if there's user info in db and hashed password matches
        if user and check_password_hash(user.password, password): 
            login_user(user)
            return redirect("/main") 

    elif request.method == 'GET':
        return render_template('signin.html')

@main.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect('/signin')
 
#######################################
###### IMAGE REPO FEATURES ############
#######################################
@main.route('/main', methods=['POST', 'GET'])
@login_required
def index():
    '''
    Default page
    '''
    g.user = current_user
    images = Image.query.filter_by(user_id=str(g.user.id)).all() # query all images in the database
    return render_template("index.html", images=images, user=current_user)

@main.route('/upload_image', methods=['POST'])
def upload_image():
    file = request.files['file'] # get the file user uploads
    # query current images in db
        
    try: # check if file extension is valid
        allowed_file(file.filename)
    except ValueError:
        flash("Invalid file extension. Please upload 'png', 'jpg', 'jpeg', 'gif'")
        return redirect('/main')

    if not file:
        raise FileNotFoundError
    filename = secure_filename(file.filename)

    # if file.unique_count not in existed_images:
    flash("Uploaded successfully!")
    image = Image(filename= filename, user_id = str(g.user.id))    
    # save that image to db
    db.session.add(image)
    db.session.commit()
    # save to /uploads directory
    file.save(os.path.join(main.config['UPLOAD_FOLDER'], image.user_id  + image.filename))
    return redirect('/main')

uploads_url = 'uploads/'
@main.route('/display/<filename_by_user>')
def display_image(filename_by_user):
    '''
    Display image in HTML
    '''
    return redirect(url_for('static', filename= uploads_url + filename_by_user), code=301)

@main.route('/delete', methods=['POST'])
def delete():
    '''
    Delete image from database 
    '''
    # get filename from HTML form
    filename_by_user = request.form.get('img_delete')
    # delete image belong to the current user
    # query based on concatenated string of two columns
    image = Image.query.filter((Image.user_id + Image.filename).like(filename_by_user)).first()
    db.session.delete(image)
    db.session.commit()
    return redirect('/main')


if __name__ == "__main__":
    main.run(debug=False)