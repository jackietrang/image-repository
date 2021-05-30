import os, re
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user, login_manager
from flask import Flask, render_template, redirect, url_for, request, g, session, flash
from flask_sqlalchemy import SQLAlchemy
import urllib.request
from werkzeug.utils import secure_filename
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
    filename = db.Column(db.String(100), nullable=True, unique=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))

class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    image_id = db.relationship('Image', backref='User')

# Creates database for users and tasks
db.create_all()
# Generates entries for the database
db.session.commit()


#######################################
########## APP CONTEXT ################
#######################################
@main.route('/', methods=['GET', 'POST'])
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
        signup_user = User(username=username, password=password) # new instance of user
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
        user = User.query.filter_by(username=username, password=password).first() #query user
        if user: # if there's user info in db, log them in
            login_user(user)
            return redirect("/main") # go to index()

    elif request.method == 'GET':
        return render_template('signin.html')
 
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
    images = Image.query.filter_by(user_id=g.user.id).all() # query all images in the database
    return render_template("index.html", images=images, user=current_user)

@main.route('/upload_image', methods=['POST'])
def upload_image():
    file = request.files['file'] # get the file user uploads
    # query current images in db
    existed_images = [image.filename for image in Image.query.all()]
        
    try: # check if file extension is valid
        allowed_file(file.filename)
    except ValueError:
        flash("Invalid file extension. Please upload 'png', 'jpg', 'jpeg', 'gif'")
        return redirect('/main')

    if file:
        filename = secure_filename(file.filename)
        if filename not in existed_images:
            flash("Uploaded successfully!")
            image = Image(filename= filename, user_id = g.user.id) 
            # save that image to db
            db.session.add(image)
            db.session.commit()
            # save to /uploads directory
            file.save(os.path.join(main.config['UPLOAD_FOLDER'], filename))
            return redirect('/main')
        # if file already existed in db
        else:
            flash('Duplicate image. Please try with another image.') 
            return redirect('/main')
    
@main.route('/display/<filename>')
def display_image(filename):
    '''
    Display image in HTML
    '''
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@main.route('/delete', methods=['POST'])
def delete():
    '''
    Delete image from database 
    '''
    # get filename from HTML form
    img_delete = request.form.get('img_delete') 
    # query and delete from db
    image = Image.query.filter_by(filename=img_delete).first()
    db.session.delete(image)
    db.session.commit()
    return redirect('/main')


if __name__ == "__main__":
    main.run(debug=False)