import os
import unittest
import sys 
import requests

class BasicTests(unittest.TestCase):
        
    def test_signup_correct(self):
        test1 = {'username':'jackie', 'password':'n123', 'repeat':'n123'} #correct signup
        request1 = requests.post('http://127.0.0.1:5000/signup', data=test1)
        self.assertEqual(request1.url,'http://127.0.0.1:5000/signin')
    
    def test_sign_in_correct(self):
        test = {'username':'jackie', 'password':'n123'} 
        request = requests.post('http://127.0.0.1:5000/signin', data=test)
        self.assertEqual(request.url,'http://127.0.0.1:5000/main')
        
    ## Comment out to see if the app detects unmatched password
    def test_signup_wrong(self):
        test2 = {'username':'one@gmail.com', 'password':'000', 'repeat':'001'} #wrong signup
        request2 = requests.post('http://127.0.0.1:5000/signup', data=test2)
        self.assertNotEqual(request2.url,'http://127.0.0.1:5000/signin')


if __name__ == "__main__":
    unittest.main()