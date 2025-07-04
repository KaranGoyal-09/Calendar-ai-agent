from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timezone
import os
import pytz
import dotenv
dotenv.load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'service_account.json')
CALENDAR_ID = os.getenv("CALENDAR_ID")

def get_calendar_service():
    """
    Authenticates and returns the Google Calendar service object.
    """
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)
    return service

def check_availability(start_time, end_time, timezone='UTC'):
    """
    Checks if the calendar is free between start_time and end_time.
    start_time and end_time should be in RFC3339 (with timezone info).
    """
    print("Checking availability between:", start_time, end_time, "Timezone:", timezone)
    try:
        service = get_calendar_service()

        # ✅ Convert to RFC3339 with explicit timezone
        from dateutil import parser, tz
        ist = tz.gettz(timezone)
        start_rfc3339 = parser.parse(start_time).astimezone(ist).isoformat()
        end_rfc3339 = parser.parse(end_time).astimezone(ist).isoformat()

        body = {
            "timeMin": start_rfc3339,
            "timeMax": end_rfc3339,
            "timeZone": timezone,
            "items": [{"id": CALENDAR_ID}]
        }

        print("Google Calendar API request body:", body)
        events_result = service.freebusy().query(body=body).execute()
        print("Google Calendar API response:", events_result)
        busy_times = events_result['calendars'][CALENDAR_ID]['busy']
        is_free = len(busy_times) == 0
        return is_free, busy_times
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Google Calendar API error:", repr(e))
        raise


def create_event(start_time, end_time, summary, description='', timezone='UTC'):
    """
    Creates a new event on the calendar.
    Args:
        start_time (str): ISO format string, e.g., '2024-06-01T10:00:00Z'
        end_time (str): ISO format string, e.g., '2024-06-01T11:00:00Z'
        summary (str): Event title
        description (str): Event description
        timezone (str): Timezone string, default 'UTC'
    Returns:
        dict: The created event object
    Raises:
        Exception: If the API call fails
    """
    print("Creating event:", start_time, end_time, summary, description, timezone)
    try:
        service = get_calendar_service()
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone,
            },
        }
        print("Google Calendar API create event body:", event)
        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        print("Google Calendar API create event response:", created_event)
        return created_event
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Google Calendar API error (create_event):", repr(e))
        raise

print("Imports successful!")

if __name__ == "__main__":
    try:
        state = {"llm": AgentState(user_input="Book Project Sync tomorrow at 10am for 1 hour.")}
        result = booking_agent.invoke(state)
        print("Final tool result:", result.get("tool_result"))
    except Exception as e:
        print("Error running agent:", str(e)) 