from __future__ import print_function
import datetime
from datetime import timedelta
import argparse
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']




def get_args():
    """"""
    parser = argparse.ArgumentParser(
        description="Google calendar api for getting information on calendar events",
        epilog="googleCal.py -n 10"
    )
    DurGroup = parser.add_argument_group('DurGroup', 'Duration by category')
    NxtGroup = parser.add_argument_group('NxtGroup', 'Next events')

    DurGroup.add_argument('-d', '--Dur', action="store",
                        help='Duration by category', default=0)
    DurGroup.add_argument('-e', '--end', action="store",
                        help='Duration End Date', default=5)
    DurGroup.add_argument('-CatDur', action='store',
                        help="Duration of event by category")
    NxtGroup.add_argument('-n', '--next', action="store",
                        help="Next Events", default=5)

    return parser.parse_args()

def nextEvents(service, numEvents):
    start = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

    events_result = service.events().list(calendarId='primary', timeMin=start,
                                maxResults=numEvents, singleEvents=True,
                                orderBy='startTime').execute()
    
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    else:
        result = events
    
    print(result)

def dur_by_cat(service, start, end):
    if start == 0:
        start = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    else:
        start = datetime.datetime.strptime(start, '%Y-%m-%d')
    
    end = start + datetime.timedelta(days=end)

    events_result = service.events().list(calendarId='primary', timeMin=start,
                                    timeMax=end, singleEvents=True,
                                    orderBy='startTime').execute()
    events = events_result.get('items', [])
    catDict = {}
    for event in events:
        start = event['start']['dateTime']
        end = event['end']['dateTime']
        eventID = event['id']
        start = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z')
        end = datetime.datetime.strptime(end, '%Y-%m-%dT%H:%M:%S%z')
        duration = end - start
        if 'colorId' in event:
            if event['colorId'] in catDict:
                catDict[event['colorId']] += duration
            else:
                catDict[event['colorId']] = duration
    
    print(catDict)

def main():

    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
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

    service = build('calendar', 'v3', credentials=creds)

    arguments = get_args()
    
    if 'CatDur' in arguments:
        dur_by_cat(service, arguments.Dur, arguments.end)
    else:
        nextEvents(service, arguments.next)

if __name__ == '__main__':
    main()