
from myapp.flask_app import app
from flask import render_template, request, redirect, make_response, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Email, required
import re
import logging
import urllib, urllib2
import json
from os import urandom
from base64 import b64encode
from myapp.models.ticketing import User, Ticket, user_key

MASHAPE_KEY = 'your-mashape-key'


class MyForm(FlaskForm):
    """ FlaskForm to retrieve user's data
        """
    name = StringField('Name', [required()])
    surname = StringField('Surname', [required()])
    email = StringField('Email', [Email, required()])
    submit = SubmitField('Generate', [required()])


@app.route('/ticket', methods=['GET'])
def showform():
    form = MyForm()
    return render_template('data.html', form=form)


@app.route('/ticket', methods=['POST'])
def submit_form():
    form = MyForm(request.form)
    if not form.validate():
        return render_template('data.html', form=form), 400

    email_inserted = form.email.data
    name_inserted = form.name.data
    surname_inserted = form.surname.data

    # verify that user's email address sintax is correct
    if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email_inserted):
        flash('Please, insert a valid email address.')
        return redirect('/ticket')
    else:
        # verify that user's email address exists through an API
        url_email = 'https://ajith-Verify-email-address-v1.p.mashape.com/varifyEmail'
        param = urllib.urlencode({'email': email_inserted})
        myurl_email = '{}?{}'.format(url_email, param)
        logging.info('my url_email: {}'.format(myurl_email))
        req = urllib2.Request(myurl_email)
        req.add_header('X-Mashape-Key', MASHAPE_KEY)
        req.add_header('Accept', 'application/json')
        urlresp = urllib2.urlopen(req)
        content = urlresp.read()
        risp = json.loads(content)
        status = risp['exist']
        print status

        if status == 'true':
            # generate random 16-bytes string
            random_bytes = urandom(16)
            token = b64encode(random_bytes).decode('utf-8')
            # use API to generate QR code
            url_qr = 'https://neutrinoapi-qr-code.p.mashape.com/qr-code'
            param2 = {
                'bg-color': '#ffffff',
                'content': token,
                'fg-color': '#000000',
                'height': 128,
                'width': 128
            }
            params = urllib.urlencode(param2)
            req2 = urllib2.Request(url_qr, params)
            req2.add_header('X-Mashape-Key', MASHAPE_KEY)
            req2.add_header('Content-Type', 'application/x-www-form-urlencoded')
            urlopen = urllib2.urlopen(req2)
            ticket_id = urlopen.read()
            resp = make_response(ticket_id)

            # save user's data in the Datastore
            qry = User.query(User.email == email_inserted).get()
            if not qry:
                newu = User(email=email_inserted)
                newu.put()
                logging.info('Correctly inserted new user {}'.format(email_inserted))
            else:
                logging.info('ok {}'.format(email_inserted))

            ticket = Ticket(parent=user_key(email_inserted), id=token, isvalid=True)
            ticket.put()
            logging.info('Correctly saved new ticket for user {}'.format(email_inserted))
            flash('Correctly generated new Ticket.')
            return redirect('/')
        else:
            flash('Please, insert an existing email address.')
            return redirect('/ticket')
