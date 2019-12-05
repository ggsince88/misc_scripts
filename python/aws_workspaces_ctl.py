import boto3
import os
import json
from time import sleep


def get_user_list(file):
    with open(file) as f:
        userlist = []
        for users in f.readlines():
            userlist.append(users.strip())
    return userlist


def get_workspaces_dict(file):
    with open(file) as f:
        dict = json.load(f)
    return dict


def get_workspaces_info(user):
    client = boto3.client('workspaces')
    workspace = get_workspaces_dict('create-workspaces.json')
    response = client.describe_workspaces(DirectoryId=workspace['DirectoryId'],
                                          UserName=user)
    return response


def create_myworkspaces(wslist):
    client = boto3.client('workspaces')
    response = client.create_workspaces(Workspaces=wslist)
    return response


def rebuild_myworkspace(wslist):
    client = boto3.client('workspaces')
    response = client.rebuild_workspaces(RebuildWorkspaceRequests=wslist)
    return response


def check_failed_requests(wsdict):
    try:
        if wsdict['FailedRequests']:
            for ws_request in wsdict['FailedRequests']:
                print('ERROR - User: {0}\n Error Message: {1}'.format(
                    ws_request['WorkspaceRequest']['UserName'],
                    ws_request['ErrorMessage']
                    ))
        else:
            print('No failed requests')
    except Exception as e:
        print(e)
        raise


def create_all_workspaces(user_file, workspace_settings_file='create-workspaces.json'):
    workspace_list = []
    for user in get_user_list(user_file):
        workspace = get_workspaces_dict(workspace_settings_file)
        workspace['UserName'] = user
        if len(workspace_list) == 25:
            # Create the first 25 workspaces. AWS limit of 25
            print(len(workspace_list))
            try:
                print('Creating {} WorkSpaces'.format(len(workspace_list)))
                response = create_myworkspaces(workspace_list)
                print(response)
                check_failed_requests(response)
                workspace_list = []
                sleep(30)
            except Exception as e:
                print(e)
                raise
        workspace_list.append(workspace)

    print('Creating {} WorkSpaces'.format(len(workspace_list)))
    response = create_myworkspaces(workspace_list)
    print(response)
    check_failed_requests(response)


def get_workspace_id(user):
    ws_dict = {'WorkspaceId': ''}
    user_ws_info = get_workspaces_info(user)
    # print(user_ws_info)
    ws_dict['WorkspaceId'] = user_ws_info['Workspaces'][0]['WorkspaceId']
    # return dict inside list per AWS documentation
    workspace_id = [ws_dict]
    return workspace_id


def rebuild_workspaces_list():
    for user in get_user_list('users_leftover.txt'):
        workspace_id = get_workspace_id(user)
        response = rebuild_myworkspace(workspace_id)
        print(response)
        print(user)


def delete_workspace(wslist):
    client = boto3.client('workspaces')
    response = client.terminate_workspaces(TerminateWorkspaceRequests=wslist)
    return response


def recreate_workspaces():
    for user in get_user_list('users.txt'):
        workspace_id = get_workspace_id(user)
        response = delete_workspace(workspace_id)
        check_failed_requests(response)
    sleep(600)
    create_all_workspaces()


def reboot_workspace(wslist):
    client = boto3.client('workspaces')
    response = client.reboot_workspaces(RebootWorkspaceRequests=wslist)
    return response


def reboot_all_workspaces():
    for user in get_user_list('all_users.txt'):
        workspace_id = get_workspace_id(user)
        response = reboot_workspace(workspace_id)
        sleep(5)
        check_failed_requests(response)


def get_workspace_connstatus(wlist):
    client = boto3.client('workspaces')
    response = client.describe_workspaces_connection_status(WorkspaceIds=wlist)
    return response


def CheckForActiveState():
    for user in get_user_list('users.txt'):
        workspace_id = get_workspace_id(user)
        wslist = [workspace_id[0]['WorkspaceId']]
        response = get_workspace_connstatus(wslist)
        if response['WorkspacesConnectionStatus'][0]['ConnectionState'] is 'CONNECTED':
            print('{0} is currently connected'.format(user))
        # print(response)


# create_all_workspaces('users10082019.txt')

for user in get_user_list('users10082019.txt'):
    try:
        info = get_workspaces_info(user)
        print(info['Workspaces'][0]['ComputerName'])
    except IndexError:
        print("An Index error was encountered with user {}".format(user))
# info = get_workspaces_info('USER')
# print(info['Workspaces'][0]['ComputerName'])
# CheckForActiveState()
#reboot_all_workspaces()
# recreate_workspaces()
# create_all_workspaces()
# rebuild_workspaces_list()
