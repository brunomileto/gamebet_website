# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""
from __future__ import print_function

import base64
import mimetypes
import smtplib
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders, errors
import os

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from flask import jsonify
from gamebet_website.app import db
from gamebet_website.app.models.models import Match, User


def check_results(match_id):
    match_for_check = Match.query.filter_by(id=match_id).first()

    if match_for_check.match_creator_match_result == 'Empate' and match_for_check.competitor_match_result == "Empate":
        match_for_check.match_status = 'EMPATE = CORRETO'
        match_for_check.save()

        match_creator_wallet_att = User.query.filter_by(id=match_for_check.match_creator_id).first()
        match_creator_wallet_att.wallet = int(match_creator_wallet_att.wallet) + int(match_for_check.bet_value)
        match_creator_wallet_att.save()

        competitor_wallet_att = User.query.filter_by(id=match_for_check.match_creator_id).first()
        competitor_wallet_att.wallet = int(competitor_wallet_att.wallet) + int(match_for_check.bet_value)
        competitor_wallet_att.save()

    else:
        match_for_check.match_status = 'ERRO - ALGUEM LANÇOU DIFERENTE'
        match_for_check.save()

    if match_for_check.match_creator_match_result == 'Vitória' and match_for_check.competitor_match_result == "Derrota":
        match_for_check.match_status = 'VITORIA CRIADOR = CORRETO'
        match_for_check.save()

        match_creator_wallet_att = User.query.filter_by(id=match_for_check.match_creator_id).first()
        match_creator_wallet_att.wallet = int(match_creator_wallet_att.wallet) + int(match_for_check.bet_value) * 2 - \
                                          int(match_for_check.bet_value * 2) * 0.1
        match_creator_wallet_att.save()


    elif match_for_check.match_creator_match_result == 'Derrota' and match_for_check.competitor_match_result == "Vitória":
        match_for_check.match_status = 'VITORIA COMPETIDOR = CORRETO'
        match_for_check.save()

        competitor_wallet_att = User.query.filter_by(id=match_for_check.match_creator_id).first()
        competitor_wallet_att.wallet = int(competitor_wallet_att.wallet) + int(match_for_check.bet_value) * 2 - \
                                          int(match_for_check.bet_value * 2) * 0.1
        competitor_wallet_att.save()

    else:
        match_for_check.match_status = 'ERRO - ALGUEM LANÇOU DIFERENTE'
        match_for_check.save()


# build a Json response
def response(data):
    return jsonify(data)
    # return app.response_class(response=json.dumps(data),
    #                           status=200,
    #                           mimetype='application/json')


def g_db_commit():
    db.session.commit()


def g_db_add(obj):
    if obj:
        db.session.add(obj)


def g_db_del(obj):
    if obj:
        db.session.delete(obj)


def send_email(path):
    # mail_content = '''Hello,
    # This is a test mail.
    # In this mail we are sending some attachments.
    # The mail is sent using Python SMTP library.
    # Thank You
    # '''
    # # The mail addresses and password
    # sender_address = 'brunomileto@outlook.com'
    # sender_pass = 'miletominarlz'
    # receiver_address = 'bruno_mileto@gmail.com'
    #
    # # Setup the MIME
    # message = MIMEMultipart()
    # message['From'] = sender_address
    # message['To'] = receiver_address
    # message['Subject'] = 'A test mail sent by Python. It has an attachment.'
    #
    # # The subject line
    # # The body and the attachments for the mail
    # message.attach(MIMEText(mail_content, 'plain'))
    # attach_file_name = path
    # attach_file = open(attach_file_name, 'rb')  # Open the file as binary mode
    # payload = MIMEBase('application', 'octate-stream')
    # payload.set_payload((attach_file).read())
    # encoders.encode_base64(payload)  # encode the attachment
    #
    # # add payload header with filename
    # payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
    # message.attach(payload)
    # # Create SMTP session for sending the mail
    # session = smtplib.SMTP_SSL('smtp.mail.outlook.com', 465)  # use gmail with port
    # session.starttls()  # enable security
    # session.login(sender_address, sender_pass)  # login with mail_id and password
    # text = message.as_string()
    # session.sendmail(sender_address, receiver_address, text)
    # session.quit()
    # print('Mail Sent')

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])

    create_message_with_attachment('brunomill3003@gmail.com', 'bruno_mileto@gmail.com', 'test', 'message test', path,
                                   service)


def create_message_with_attachment(
        sender, to, subject, message_text, file, service):
    """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.
    file: The path to the file to be attached.

  Returns:
    An object containing a base64url encoded email object.
  """

    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    message.attach(MIMEText(message_text, 'plain'))
    attach_file_name = file
    attach_file = open(attach_file_name, 'rb')  # Open the file as binary mode
    payload = MIMEBase('application', 'octate-stream')
    payload.set_payload(attach_file.read())
    encoders.encode_base64(payload)  # encode the attachment

    payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
    message.attach(payload)

    text = message.as_string()
    return send_message(service, 'me', text)


def send_message(service, user_id, message):
    """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

# def create_draft(service, user_id, message_body):
#     try:
#         message = {'message': message_body}
#         draft = service.users().drafts().create(userId=user_id, body=message).execute()
#
#         print("Draft id: %s\nDraft message: %s" % (draft['id'], draft['message']))
#
#         return draft
#     except Exception as e:
#         print('An error occurred: %s' % e)
#         return None
