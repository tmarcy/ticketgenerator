
from myapp.flask_app import app, csrf_protect
from flask import request, make_response
from myapp.models.ticketing import User, Ticket, user_key
import json
import logging


def raise_error(message='An error occured during a request', errcode=500):
    json_response = {}
    json_response['data'] = []
    json_response['status'] = 'Failure'
    json_response['message'] = message
    risp = make_response(json.dumps(json_response, ensure_ascii=True), errcode)
    risp.headers['content-type'] = 'application/json'
    return risp


@app.route('/api/v1.0/ticket', methods=['GET'])
def getlist():
    params = request.args
    required_parameters = ['email']

    for r in required_parameters:
        if r not in params:
            return raise_error(message = 'Missing {} parameter'.format(r), errcode=400)

    email_inserted = request.args.get('email')

    # Search for user in the Datastore and retrieve his tickets
    qry = User.query(User.email==email_inserted).get()
    if not qry:
        return raise_error(message='Email inserted is not present in our database.')
    else:
        qry2 = Ticket.query(ancestor=user_key(email_inserted)).fetch()

        mydata = []
        for each in qry2:
            dicdata = {}
            dicdata['Ticket id'] = each.id
            dicdata['isvalid'] = each.isvalid
            mydata.append(dicdata)

        # status of the json_response
        json_response = {}
        json_response['data'] = mydata
        json_response['status'] = 'OK'
        json_response['message'] = 'Successfully returned the resource.'
        risp = make_response(json.dumps(json_response, ensure_ascii=True), 200)
        risp.headers['content-type'] = 'application/json'
        return risp


@csrf_protect.exempt
@app.route('/api/v1.0/ticket', methods=['POST'])
def insert_ticket():
    params = request.args
    required_parameters = ['email', 'ticket_id']

    for r in required_parameters:
        if r not in params:
            return raise_error(message='Missing {} parameter'.format(r), errcode=400)

    email_inserted = request.args.get('email')
    ticket_id_inserted = request.args.get('ticket_id')

    # save data in the Datastore
    qry = User.query(User.email == email_inserted).get()
    if not qry:
        newu = User(email=email_inserted)
        newu.put()
        logging.info('Correctly inserted new user {}'.format(email_inserted))
    else:
        logging.info('ok {}'.format(email_inserted))

    ticket = Ticket(parent=user_key(email_inserted), id=ticket_id_inserted, isvalid=True)
    ticket.put()
    logging.info('Correctly saved new ticket for user {}'.format(email_inserted))

    # status of the json_response
    json_response = {}
    json_response['data'] = []
    json_response['status'] = 'OK'
    json_response['message'] = 'Correctly generated ticket.'
    risp = make_response(json.dumps(json_response, ensure_ascii=True), 200)
    risp.headers['content-type'] = 'application/json'
    return risp


@app.route('/api/v1.0/validate_ticket', methods=['GET'])
def validate_ticket():
    params = request.args
    required_parameters = ['email', 'ticket_id']

    for r in required_parameters:
        if r not in params:
            return raise_error(message='Missing {} parameter'.format(r), errcode=400)

    email_inserted = request.args.get('email')
    ticket_id = request.args.get('ticket_id')

    # Search for user in the Datastore and retrieve his tickets
    qry = User.query(User.email == email_inserted).get()
    if not qry:
        return raise_error(message='Email inserted is not present in our database.')
    else:
        qry2 = Ticket.query(ancestor=user_key(email_inserted)).fetch()
        mydata = []
        for each in qry2:
            if each.id == ticket_id:
                dicdata = {}
                dicdata['Ticket id'] = each.id
                if each.isvalid is True:
                    dicdata['isvalid'] = 1
                    dicdata['message'] = 'This ticket is valid.'
                else:
                    dicdata['isvalid'] = 0
                    dicdata['message'] = 'This ticket is NOT valid.'
                mydata.append(dicdata)

        # status of the json_response
        json_response = {}
        json_response['data'] = mydata
        json_response['status'] = 'OK'
        json_response['message'] = 'Successfully returned the resource.'
        risp = make_response(json.dumps(json_response, ensure_ascii=True), 200)
        risp.headers['content-type'] = 'application/json'
        return risp
