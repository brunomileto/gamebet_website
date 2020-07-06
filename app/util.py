# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""
from __future__ import print_function

import base64
import mimetypes
import smtplib
from datetime import date
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
from sqlalchemy import or_, and_

from gamebet_website.app import db
from gamebet_website.app.models.models import Match, User, SiteFinance
from PIL import Image


def check_results(match_id):
    match_for_check = Match.query.filter_by(id=match_id).first()

    if match_for_check.match_creator_match_result == 'Empate' and match_for_check.competitor_match_result == "Empate":
        match_for_check.match_status = 'Empate'
        match_for_check.match_end_date = date.today()
        match_for_check.save()

        match_creator_wallet_att = User.query.filter_by(id=match_for_check.match_creator_id).first()
        match_creator_wallet_att.wallet = int(match_creator_wallet_att.wallet) + int(match_for_check.bet_value)
        match_creator_wallet_att.save()

        competitor_wallet_att = User.query.filter_by(id=match_for_check.match_creator_id).first()
        competitor_wallet_att.wallet = int(competitor_wallet_att.wallet) + int(match_for_check.bet_value)
        competitor_wallet_att.save()

    else:
        match_for_check.match_status = 'Em Análise'
        match_for_check.save()

    if match_for_check.match_creator_match_result == 'Vitória' and match_for_check.competitor_match_result == "Derrota":
        match_for_check.match_status = match_for_check.match_creator_gametag
        match_for_check.match_end_date = date.today()
        match_for_check.save()

        site_commission = int(match_for_check.bet_value * 2) * 0.1

        match_creator_wallet_att = User.query.filter_by(id=match_for_check.match_creator_id).first()
        match_creator_wallet_att.wallet = int(match_creator_wallet_att.wallet) + int(match_for_check.bet_value) * 2 - \
                                          site_commission
        match_creator_wallet_att.save()
        commission_date = date.today()
        new_commission = SiteFinance(match_id=match_for_check.id, match_bet_value=match_for_check.bet_value,
                                     match_total_value=match_for_check.bet_value*2, commission_value=site_commission,
                                     match_winner_user=match_for_check.match_creator_username,
                                     commission_date=commission_date)
        new_commission.save()

    elif match_for_check.match_creator_match_result == 'Derrota' and match_for_check.competitor_match_result == "Vitória":
        match_for_check.match_status = match_for_check.competitor_gametag
        match_for_check.match_end_date = date.today()
        match_for_check.save()

        site_commission = int(match_for_check.bet_value * 2) * 0.1

        competitor_wallet_att = User.query.filter_by(id=match_for_check.competitor_id).first()
        competitor_wallet_att.wallet = int(competitor_wallet_att.wallet) + int(match_for_check.bet_value) * 2 - \
                                       site_commission
        competitor_wallet_att.save()
        commission_date = date.today()
        new_commission = SiteFinance(match_id=match_for_check.id, match_bet_value=match_for_check.bet_value,
                                     match_total_value=match_for_check.bet_value*2, commission_value=site_commission,
                                     match_winner_user=match_for_check.match_creator_username,
                                     commission_date=commission_date)
        new_commission.save()

    else:
        match_for_check.match_status = "Em Análise"
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


def save_image(image, image_path, complete_path):
    if not os.path.isdir(image_path):
        print('criando diretorio')
        os.makedirs(image_path)
    try:
        print('removendo imagem, se existir')
        os.remove(complete_path)

    except Exception as err:
        print(err)
    print('salvando imagem')
    image.save(complete_path)


def open_image(image_path):
    img = Image.open(image_path)
    img.show()


def basic_user_statistics(id):
    user = User.query.filter_by(id=id).first()
    actual_user_wallet = user.wallet

    finished_matches = Match.query.filter(or_(Match.match_creator_id == int(id),
                                              Match.competitor_id == int(id))).filter(
        and_(Match.match_status != "Procurando", Match.match_status != "Aguardando",
             Match.match_status != "Em Análise", Match.match_status != "Em Partida")).count()

    opened_matches = Match.query.filter(
        or_(Match.match_creator_id == int(id), Match.competitor_id == int(id))).filter(
        or_(Match.match_status == "Em Partida", Match.match_status == "Aguardando")).count()
    print(finished_matches)
    print(opened_matches)
    print('hey')
    return [actual_user_wallet, finished_matches, opened_matches]


def get_matches_data(matches):
    today = date.today()
    current_week = today.isocalendar()[1]
    weeks = list(range(current_week - 11, current_week + 1))
    match_creation_weeks = []
    for match in matches:
        if match.match_creation_date:
            print(match.match_creation_date)
            print(type(match.match_creation_date))
            match_creation_week = match.match_creation_date.isocalendar()[1]
            match_creation_weeks.append(match_creation_week)
    match_creation_week_results = []
    for week in weeks:
        match_creation_week_results.append(match_creation_weeks.count(week))
    labels = weeks
    results = match_creation_week_results
    return labels, results


def get_finance_data(datas):
    today = date.today()
    current_week = today.isocalendar()[1]
    weeks = list(range(current_week - 11, current_week + 1))
    datas_weeks = []
    for data in datas:
        try:
            if data.commission_date:
                print(data.commission_date)
                data_week = data.commission_date.isocalendar()[1]
                datas_weeks.append(data_week)
        except:
            try:
                if data.sale_date:
                    print(data.sale_date.date())
                    data_week = data.sale_date.isocalendar()[1]
                    datas_weeks.append(data_week)
            except:
                if data.order_end_date:
                    print(data.order_end_date)
                    data_week = data.order_end_date.isocalendar()[1]
                    datas_weeks.append(data_week)

    data_week_results = []
    for week in weeks:
        data_week_results.append(datas_weeks.count(week))
    labels = weeks
    print(labels)
    results = data_week_results
    return labels, results


def site_finance(class_instance):
    total_commission = 0
    for commission in class_instance:
        total_commission += commission.commission_value

    total_commission = f'{total_commission:.2f}'
    total_commission = str(total_commission)
    total_commission = total_commission.replace('.', ',')
    return total_commission


def site_sales(class_instance):
    total_sales = 0
    for sale in class_instance:
        total_sales += sale.product_value

    total_sales = f'{total_sales:.2f}'
    total_sales = str(total_sales)
    total_sales = total_sales.replace('.', ',')
    return total_sales


def total_money_requests(class_instance):
    total_requests = 0
    for money_request in class_instance:
        total_requests += money_request.value_wanted

    total_requests = f'{total_requests:.2f}'
    total_requests = str(total_requests)
    total_requests = total_requests.replace('.', ',')
    print(total_requests)
    print('aqqqqui')
    return total_requests


def stored_choice(choice, choice_list):
    for i in range(len(choice_list)):
        if choice in choice_list[i]:
            choice_default = i
            return choice_default


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
