#!/usr/bin/python 
# defining a function return hashed password 
  
from streamlit_authenticator.utilities.hasher import Hasher
import sys
  
class PasswordGenerator: 
    
    argumentList = sys.argv
    
    if argumentList[0].endswith('.py'):
        argumentList.pop(0)
        
    print(argumentList)
    hashed_password = Hasher(argumentList).generate()
    print (hashed_password)