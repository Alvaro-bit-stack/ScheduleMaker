import datetime as dt
import os.path
import random as rd
from usage import classes_list
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]
WEEKDAY_MAP = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}

def get_first_occurrence(start_date, target_day):
    """Find the first date >= start_date that matches the target weekday."""
    start_weekday = start_date.weekday()
    target_weekday = WEEKDAY_MAP[target_day]
    days_ahead = (target_weekday - start_weekday) % 7
    return start_date + dt.timedelta(days=days_ahead)

def main():
    creds = None
    # use cred to auth ourselves use the token so everytime we use it we dont have to verify creds
    # if tokens dont exist we have to make it
    if os.path.exists("token.json"):
        # if the token exists just load it 
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        # make the token if it doesnt exist
        else:
            flow = InstalledAppFlow.from_client_secrets_file("creds.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        # build the service
        service = build("calendar","v3",credentials=creds)
        #Commmented out b/c ts for getting events
        """ 
        # get the current time in UTC
        now = dt.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        
        # get the next 10 upcoming events
        events_result = service.events().list(
            calendarId="primary",  # correct param name
            timeMin=now,
            maxResults=10,
            singleEvents=True,     # correct param name
            orderBy="startTime"    # correct param name
        ).execute()
        
        events = events_result.get("items", [])
        
        if not events:
            print("No upcoming events found")
            return
        
        # print the start and name of the event
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"]) """
        semester_start = dt.date(2025, 9, 1)
        semester_end = "20251231T235959Z"
        for class_info in classes_list:
            class_name = class_info["class_name"]
            days = class_info["days"]
            start_time = class_info["start_time"]
            end_time = class_info["end_time"]
            location = class_info["location"]
            colorId = rd.randint(1, 11)
            first_day = min(days, key=lambda d: WEEKDAY_MAP[d])
            first_date = get_first_occurrence(semester_start, first_day)
            start_dt = dt.datetime.strptime(f"{first_date} {start_time}", "%Y-%m-%d %I:%M %p")
            end_dt = dt.datetime.strptime(f"{first_date} {end_time}", "%Y-%m-%d %I:%M %p")
            event = {
                "summary": class_name,
                "location": location,
                "colorId": str(colorId),
                "start": {
                    "dateTime": start_dt.isoformat(),                      
                    "timeZone": "America/New_York",
                },
                "end": {
                    "dateTime": end_dt.isoformat(),
                    "timeZone": "America/New_York",
                },
                "recurrence": [
                    f"RRULE:FREQ=WEEKLY;BYDAY={','.join(days)};UNTIL={semester_end}",
                ],
            }
            event =  service.events().insert(calendarId="primary", body=event).execute()
            print(f"Event created: {event.get('htmlLink')}")
    except HttpError as error:
        print("An error occured:", error)

if __name__ == "__main__":
    main()
