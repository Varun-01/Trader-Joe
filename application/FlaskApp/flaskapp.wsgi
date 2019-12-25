#!/usr/bin/python3.6
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/home/csc648-fall2019-Team13/application/FlaskApp/")

from FlaskApp import app as application
application.secret_key = 'asdsafasfad'
