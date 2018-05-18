
from flask import render_template

from myapp import app


@app.route('/')
def homepage():
    handlers = [
        ('generate ticket', '/ticket'),
        ('my ticket', '/api/v1.0/ticket'),
        ('isvalid?', '/api/v1.0/validate_ticket')]

    return render_template('home.html', handlers=handlers)

