import os, sys
# Bring  packages onto the path
import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))

import unittest
import requests
import app 
from app import main


class BasicTests(unittest.TestCase):
        
    def test_signup_correct(self):
        '''
        After signing up, user should be routed to sign-in 
        '''
        test = {'username':'jackie', 'password':'n123', 'repeat':'n123'} #correct signup
        request = requests.post('http://127.0.0.1:5000/signup', data=test)
        self.assertEqual(request.url,'http://127.0.0.1:5000/signin')
    
    def test_sign_in_correct(self):
        '''
        After successful sign-in, user should be routed to the main page
        '''
        test = {'username':'jackie', 'password':'n123'} 
        request = requests.post('http://127.0.0.1:5000/signin', data=test)
        self.assertEqual(request.url,'http://127.0.0.1:5000/main')
        
    def test_signup_invalid_password(self):
        '''
        Not sign-in user the password doesn't meet 
        the criterion of having both numbers and letters
        '''
        password_list = ["000", "aaaa"] 
        for password in password_list:
            test = {'username':'one@gmail.com', 'password': password, 'repeat': password} 
            request = requests.post('http://127.0.0.1:5000/signup', data = test)
            self.assertNotEqual(request.url,'http://127.0.0.1:5000/signin')
    
    def test_password_not_match(self):
        '''
        Not sign-in if password doesn't match repeated password in sign-up
        '''
        password_list = ["n123", "a32", "032aj"] 
        for password in password_list:
            test = {'username':'one@gmail.com', 'password': password, 'repeat': "random_pass"} 
            request = requests.post('http://127.0.0.1:5000/signup', data=test)
            self.assertNotEqual(request.url,'http://127.0.0.1:5000/signin')
    

    def test_file_existence(self):
        '''
        Uploading invalid files should raise a ValueError
        '''
        test = {'file':None} #correct signup
        url = 'http://127.0.0.1:5000/upload_image'
        with main.test_client() as c:
            response = c.post(url, json=test)
            self.assertRaises(FileNotFoundError)

if __name__ == "__main__":
    unittest.main()