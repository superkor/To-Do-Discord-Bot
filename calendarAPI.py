from __future__ import print_function
import datetime
import os.path
from re import T

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class InvalidCredentials(Exception):
    """Exception raised for invalid Credentials or no credential.json file provided"""
    def __init__(self, message="Invalid Credentials or no credential.json file provided"):
        self.message = message
        super().__init__(self.message)

def main():
    #Initializes API
    global creds
    creds = None
    valid = False
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        valid = True
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            print("Calendar API loaded credentials!")
            valid = True
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                print("Calendar API loaded credentials!")
                valid = True
            except FileNotFoundError:
                print("Cannot find credentials.json!")
                raise InvalidCredentials
    if (valid):
        try:    
            global service 
            service = build('calendar', 'v3', credentials=creds)
            global calID
            file = open("calID.txt", "r")
            calID = file.readline()

            """ event = {
                "summary": "test", 
                "location": "this is a test", 
                "description": "desc", 
                "start": 
                {"dateTime": "2022-04-24T21:00:00-04:00", "timeZone": "America/Toronto"},
                "end": 
                {"dateTime": "2022-04-25T08:00:00-04:00", "timeZone": "America/Toronto"}, 
                "reminders": 
                    {'useDefault': False, "overrides": [{"method": "popup", "minutes": 60}]}    
            }      
            event = service.events().insert(calendarId=calID, body=event).execute()
            print ('Event created: %s' % (event.get('htmlLink'))) """
            print("Calendar API ready!")
        except HttpError as error:
            print('An error occurred: %s' % error)
"""
createEvent() gets event JSON from main.newEvent() and creates the event on google calendar
"""
def createEvent(event):
    try:
        event = service.events().insert(calendarId=calID, body=event).execute()
        print ('Event created: %s' % (event.get('htmlLink')))
        return event.get('htmlLink')
    except HttpError as error:
        print('An error occurred: %s' % error)
        return error

def listEvents():
    try:
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId=calID, timeMin=now,
                                              maxResults=6, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            return None
        else:
            return events

    except HttpError as error:
        print('An error occurred: %s' % error)
        return error

if __name__ == '__main__':
    main()