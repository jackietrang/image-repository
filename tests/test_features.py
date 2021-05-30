import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))

# Now do your import
import pytest 
import app 
from flask import request
import requests
from app import main


@pytest.mark.parametrize("file_name", [".mp3", ".mp4", ".pdf", ".doc", ".docx"])
def test_valid_file(file_name):
    '''
    Uploading invalid files should raise a ValueError
    '''
    with pytest.raises(ValueError, match=r"Invalid file extension. Please upload 'png', 'jpg', 'jpeg', 'gif'"):
        app.allowed_file(file_name)



