from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from backend.calendar_utils import create_event, check_availability
# Import the agent conversation function
from agent.booking_agent import run_agent_conversation
import traceback
import pytz

app = FastAPI()

class BookingRequest(BaseModel):
    summary: str
    start: datetime = Field(..., description="Start time in RFC3339 format")
    end: datetime = Field(..., description="End time in RFC3339 format")
    description: Optional[str] = None

    def validate_times(self):
        if self.start >= self.end:
            raise ValueError("Start time must be before end time.")

# --- New: Chat endpoint ---
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    print("Received /chat request with message:", request.message)
    try:
        reply = run_agent_conversation(request.message)
        print("Agent reply:", reply)
        return ChatResponse(response=reply)
    except Exception as e:
        traceback.print_exc()
        print("Error in /chat endpoint:", e)
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

class BookingResponse(BaseModel):
    status: str
    event: Optional[Dict[str, Any]] = None
    busy_slots: Optional[List[Any]] = None
    message: Optional[str] = None

@app.post("/book", response_model=BookingResponse)
async def book_event(request: BookingRequest):
    try:
        request.validate_times()
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    # Convert datetimes to Asia/Kolkata timezone and RFC3339 string
    ist = pytz.timezone('Asia/Kolkata')
    start_ist = request.start.astimezone(ist)
    end_ist = request.end.astimezone(ist)
    start_str = start_ist.strftime('%Y-%m-%dT%H:%M:%S')
    end_str = end_ist.strftime('%Y-%m-%dT%H:%M:%S')
    timezone = 'Asia/Kolkata'
    try:
        # Check availability
        is_free, busy_info = check_availability(start_str, end_str, timezone)
        if not is_free:
            return BookingResponse(status="busy", busy_slots=busy_info, message="Time slot is busy.")
        # Book the event
        event = create_event(start_str, end_str, request.summary, request.description, timezone)
        if isinstance(event, dict) and event.get("id"):
            return BookingResponse(status="booked", event=event, message="Event booked successfully.")
        else:
            return BookingResponse(status="error", message="Unknown error booking event.")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})

