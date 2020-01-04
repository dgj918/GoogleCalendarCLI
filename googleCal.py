from __future__ import print_function
import datetime
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

    parser.add_argument('-n', '--numEvents', action="store",
                        help='Number of events to return')

    return parser.parse_args()

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

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    arguments = get_args()
    print(arguments)
    print('Getting the upcoming ' + str(arguments.numEvents) + ' events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=arguments.numEvents, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start']['dateTime']
        end = event['end']['dateTime']
        eventID = event['id']
        start = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z')
        end = datetime.datetime.strptime(end, '%Y-%m-%dT%H:%M:%S%z')
        duration = end - start

        eventDetail = service.events().get(calendarId='primary', eventId=eventID).execute()
        print(eventDetail)



if __name__ == '__main__':
    main()