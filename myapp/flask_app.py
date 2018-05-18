
import logging

from flask import Flask
from flask_wtf.csrf import CSRFProtect

import myapp.app_config
import appengine_config


app = Flask(__name__)
app.config.from_object(__name__)

if appengine_config.GAE_DEV:
    logging.info('Using a dummy secret key.')
    app.secret_key = 'my-secret-key'
    app.debug = True
else:
    app.secret_key = myapp.app_config.app_secure_key

DEBUG = True
csrf_protect = CSRFProtect(app)


