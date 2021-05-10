# Image Repository Challenge by Jackie Trang
Built an image repository that allows uploading images and deleting images using Flask framework and SQLite database.

## Features
1. Sign up new user
2. Log in existing user
3. Upload images after checking whether the image is unique and has a valid extension
4. Delete images

## Project Structure
+ README.md
+ app.py
+ unittests.py #tests for the application
+ database.db #sqlite database
+ requirements.txt
+ templates
    + index.html
    + signin.html
    + signup.html
+ static
    + uploads # folder to store images uploaded
    + style.css

## How to run the app
### Windows 
1. Clone this repository to local computer
2. Set up virtual environment and install dependencies 
```sh
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```
4. Go back to the directory because we're at activate file directory now
```sh
cd ../.. # go up two levels
```
3. Set up database (main directory)
```sh
python #activate Python shell
from app import db
db.create_all()
exit()
```
4. Run the application
```sh
python app.py
```
The app will be running on ``` http://127.0.0.1:5000/ ``` in your web browser.

### MacOS
Step 1, 3, 4 are similar to Windows.
The only difference is in activating virtual environment (step 2):
```sh
python3.6 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```
## How to run unit test 
<strong>Note: </strong> Make sure the app is running when test files are executed. This can be done by having split terminals in IDE.
For authentication (signup, login):
```sh
python unittests.py
```

## Project Demo
Here's a walkthrough of the app:

<img src='projec_demo.gif' title='Video Walkthrough' width='' alt='Video Walkthrough' />

GIF created with [LiceCap](http://www.cockos.com/licecap/).
