
import os

from google.appengine.ext import vendor
vendor.add('lib')

if os.getenv('SERVER SOFTWARE', '').startswith('Google App Engine/'):
    GAE_DEV = False
else:
    GAE_DEV = True

