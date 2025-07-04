from calendar_utils import get_calendar_service, check_availability, create_event
from datetime import datetime, timedelta
import pytz

# Update these before running
timezone = 'UTC'
start_time = (datetime.utcnow() + timedelta(minutes=5)).replace(second=0, microsecond=0).isoformat() + 'Z'
end_time = (datetime.utcnow() + timedelta(minutes=35)).replace(second=0, microsecond=0).isoformat() + 'Z'

print("Testing Google Calendar integration...")

try:
    # Test authentication
    service = get_calendar_service()
    print("✅ Authenticated with Google Calendar API.")

    # Test availability
    is_free = check_availability(start_time, end_time, timezone)
    print(f"Availability from {start_time} to {end_time}: {'Free' if is_free else 'Busy'}")

    # Test event creation if free
    if is_free:
        event_link = create_event(start_time, end_time, summary="Test Booking", description="This is a test event.", timezone=timezone)
        print(f"✅ Event created: {event_link}")
    else:
        print("❌ Time slot is busy, not creating event.")
except Exception as e:
    print("❌ Error during test:", e)

print("\nMake sure you have updated CALENDAR_ID in calendar_utils.py and placed your credentials.json file in backend/.") 

def check_availability(start_time, end_time, timezone='UTC'):
    try:
        service = get_calendar_service()
        body = {
            "timeMin": start_time,
            "timeMax": end_time,
            "timeZone": timezone,
            "items": [{"id": CALENDAR_ID}]
        }
        events_result = service.freebusy().query(body=body).execute()
        busy_times = events_result['calendars'][CALENDAR_ID]['busy']
        return len(busy_times) == 0
    except Exception as e:
        print("Google Calendar API error:", repr(e))
        return f"ERROR: {repr(e)}"

start = "2025-07-10T15:00:00Z"
end = "2025-07-10T16:00:00Z"
print(check_availability(start, end)) 