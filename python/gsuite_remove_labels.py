from __future__ import print_function
import httplib2
import time

from apiclient import discovery
from apiclient import errors
from oauth2client import service_account, clientsecrets, tools, client

try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = ['https://mail.google.com/',
          'https://www.googleapis.com/auth/admin.directory.user.readonly']
CLIENT_SECRET_FILE = 'client_secret.json'
SERVICE_ACCOUNT_FILE = 'service_secret.json'
APPLICATION_NAME = 'Clean Up labels '



# Get service account credentials with domain wide permissions
def auth_google(google_service, api_version, account_sub):
    credentials = service_account.ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    delegated_credentials = service_account.ServiceAccountCredentials.create_delegated(credentials, account_sub)
    http = delegated_credentials.authorize(httplib2.Http())
    connect_google = discovery.build(google_service, api_version, http=http)
    return connect_google


def list_messages_with_labels(service, user_id, label_ids=[]):
    try:
        response = service.users().messages().list(userId=user_id,
                                                   labelIds=label_ids).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id,
                                                       labelIds=label_ids,
                                                       pageToken=page_token).execute()
            messages.extend(response['messages'])
            if len(messages) > 999:
                break

        return messages
    except errors.HttpError:
        print(errors.HttpError)


def batch_delete_messages(service, user_id, messages):
    print("ready to delete {} messages,,,".format(len(messages['ids'])))

    try:
        service.users().messages().batchDelete(
            userId=user_id,
            body=messages
        ).execute()
    except errors.HttpError:
        print('An error occurred while batchDeleting: {0}'.format(errors.HttpError))


def format_message_ids(raw_messages):
    message = {
        'ids': []
    }
    message['ids'].extend([str(d['id']) for d in raw_messages])
    return message


def delete_label(service, user_id, label_id):
    try:
        service.users().labels().delete(userId=user_id, id=label_id).execute()
    except errors.HttpError:
        print(errors.HttpError)


def get_labels(service, user_id):
    try:
        results = service.users().labels().list(userId=user_id).execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found,,,')
        else:
            return labels
    except errors.HttpError:
        print(errors.HttpError)


def ListMessagesMatchingQuery(service, user_id, query=''):
    response = service.users().messages().list(userId=user_id,
                                               q=query).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,
                                         pageToken=page_token).execute()
      messages.extend(response['messages'])
    return messages


def main():
    user = 'USER@TEST.COM'
    response = auth_google('gmail', 'v1', user)
    labels = get_labels(response, user)

    for label in labels:
        if label['name'].startswith('001 - Current & Future'):
            # print(label['name'])
            continue
        elif label['name'].startswith('001 - AR/AP/Payroll Related'):
            # print('Found it! {0}'.format(label['name']))
            continue
        elif label['type'] == 'system':
            # print('Found system label!')
            continue
        results = response.users().labels().get(id=label['id'], userId=user).execute()
        print('before,{0},{1},{2}'.format(results['id'], results['name'], results['messagesTotal']))
        msg_ids = list_messages_with_labels(response, user, label['id'])
        if msg_ids:
            batch_delete_messages(response, user, format_message_ids(msg_ids))
            time.sleep(1)
            results = response.users().labels().get(id=label['id'], userId=user).execute()
            print('after,{0},{1},{2}'.format(results['id'], results['name'], results['messagesTotal']))
        if results['messagesTotal'] == 0:
            delete_label(response, user, label['id'])


if __name__ == '__main__':
    main()
