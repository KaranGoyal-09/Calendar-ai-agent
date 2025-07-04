"""
Conversational AI agent for booking Google Calendar appointments.
Uses Langchain to understand user intent, check availability, and create events via direct tool calls.
"""

import os
from langchain.agents import initialize_agent, Tool, AgentType
from backend.calendar_utils import check_availability, create_event
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from dateutil import parser, tz
from langchain_core.prompts import ChatPromptTemplate

# 1. Define tools for the agent

def tool_check_availability(query: str) -> str:
    """Check if a time slot is available. Expects query to be 'start_time|end_time|timezone'"""
    print("tool_check_availability called with:", query)
    try:
        start_time, end_time, *_ = query.split('|')
        # Always use Asia/Kolkata timezone
        ist = tz.gettz('Asia/Kolkata')
        if "T" not in start_time:
            start_time = parser.parse(start_time).replace(tzinfo=ist).strftime('%Y-%m-%dT%H:%M:%S')
        if "T" not in end_time:
            end_time = parser.parse(end_time).replace(tzinfo=ist).strftime('%Y-%m-%dT%H:%M:%S')
        timezone = 'Asia/Kolkata'
        print("Parsed times:", start_time, end_time, timezone)
        is_free, busy_info = check_availability(start_time, end_time, timezone)
        print("tool_check_availability result:", is_free, busy_info)
        if is_free:
            return "The time slot is available."
        else:
            return f"The time slot is busy. Busy slots: {busy_info}"
    except Exception as e:
        print("tool_check_availability exception:", repr(e))
        return f"Error checking availability: {e}"

def tool_create_event(query: str) -> str:
    """Create a calendar event. Expects query to be 'start_time|end_time|summary|description|timezone'"""
    print("tool_create_event called with:", query)
    try:
        start_time, end_time, summary, description, *_ = query.split('|')
        # Always use Asia/Kolkata timezone
        ist = tz.gettz('Asia/Kolkata')
        if "T" not in start_time:
            start_time = parser.parse(start_time).replace(tzinfo=ist).strftime('%Y-%m-%dT%H:%M:%S')
        if "T" not in end_time:
            end_time = parser.parse(end_time).replace(tzinfo=ist).strftime('%Y-%m-%dT%H:%M:%S')
        timezone = 'Asia/Kolkata'
        print("Parsed times:", start_time, end_time, summary, description, timezone)
        event = create_event(start_time, end_time, summary, description, timezone)
        print("tool_create_event result:", event)
        if isinstance(event, dict) and event.get("htmlLink"):
            return f"Event created successfully! Link: {event['htmlLink']}"
        else:
            return "Event creation failed."
    except Exception as e:
        print("tool_create_event exception:", repr(e))
        return f"Error creating event: {e}"

# 2. Register tools

tools = [
    Tool(
        name="CheckAvailability",
        func=tool_check_availability,
        description="Check if a time slot is available. Input: 'start_time|end_time|timezone'"
    ),
    Tool(
        name="CreateEvent",
        func=tool_create_event,
        description="Create a calendar event. Input: 'start_time|end_time|summary|description|timezone'"
    )
]

# 3. Initialize the Gemini LLM and agent (using a model you have access to)

load_dotenv()
# Update Gemini API key and model
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(google_api_key=GEMINI_API_KEY, model="models/gemini-2.0-flash")

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 4. Function to extract event parameters from conversation history
def extract_event_parameters(conversation_history: list) -> tuple:
    """
    Uses Gemini to extract event parameters from the conversation history.
    Always returns a tuple: (params_dict, raw_gemini_output_or_error_message)
    """
    from datetime import datetime
    import json
    import re

    def safe_extract_json(text: str) -> dict:
        """
        Attempts to safely extract a JSON object from Gemini's text output.
        Handles code blocks and extra whitespace.
        """
        import re
        import json

        try:
            print("\n--- Raw Gemini Response Start ---")
            print(text)
            print("--- Raw Gemini Response End ---\n")

            # Strip code block markers and extra spaces
            text = re.sub(r"^```(json)?", "", text.strip(), flags=re.IGNORECASE | re.MULTILINE)
            text = re.sub(r"```$", "", text.strip(), flags=re.MULTILINE)
            text = text.strip()

            # Extract just the first JSON object (non-greedy match)
            match = re.search(r"\{[\s\S]*?\}", text)
            if not match:
                raise ValueError("No JSON object found in Gemini output.")

            json_str = match.group(0).strip()
            print("[Clean JSON string]:", json_str)
            return json.loads(json_str)

        except Exception as e:
            print("[safe_extract_json Error]", e)
            raise


    try:
        today = datetime.now().strftime('%Y-%m-%d')
        transcript = "\n".join([
            ("User: " + m["content"]) if m["role"] == "user" else ("Assistant: " + m["content"]) for m in conversation_history
        ])

        system_prompt = (
            f"You are a helpful assistant that extracts event details from a chat transcript for Google Calendar booking. "
            f"Today's date is {today}. Always return ONLY a valid JSON object with keys: summary, date (YYYY-MM-DD), start_time (HH:MM, 24h), end_time (HH:MM, 24h), and description. "
            "Do not include any explanation, markdown, or formatting—just the JSON. "
            "If any field is missing or ambiguous, set its value to 'MISSING'. Infer missing details from the conversation context if possible."
        )

        from langchain_core.prompts import ChatPromptTemplate
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", f"Here is the chat transcript:\n{transcript}\nExtract the event details as JSON.")
        ])

        formatted_prompt = prompt.format_messages(transcript=transcript)
        response = llm.invoke(formatted_prompt)

        # ✅ Extract only the clean content
        raw = response.content if hasattr(response, 'content') else str(response)

        print("[Gemini Raw Output]:", raw)

        params = safe_extract_json(raw)
        print("[Extracted Params]:", params)
        return params, raw
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {}, f"[extract_event_parameters Exception] {e}"


# 5. Main function to handle the workflow

def run_agent_conversation(user_message: str, conversation_history: list = None) -> str:
    print(f"[Agent] Received user message: {user_message}")
    if conversation_history is None:
        # Fallback to single-turn if no history is provided
        conversation_history = [{"role": "user", "content": user_message}]
    params, raw_gemini = {}, ""
    try:
        params, raw_gemini = extract_event_parameters(conversation_history)
        print(f"[Agent] (DEBUG) params: {params}")
        print(f"[Agent] (DEBUG) raw_gemini: {raw_gemini}")
        required = ["summary", "date", "start_time", "end_time"]
        # Robust type and key checks
        if not isinstance(params, dict):
            return (
                "Sorry, I couldn't understand the details from your message.\n"
                f"Extracted parameters (not a dict): {params}\n"
                f"Raw Gemini output: {raw_gemini}\n"
                "Please try rephrasing your request or provide more details."
            )
        missing = [k for k in required if not params.get(k) or params[k] == 'MISSING']
        if missing:
            pretty = {
                "summary": "what the event is about",
                "date": "the date of the event",
                "start_time": "when the event starts",
                "end_time": "when the event ends"
            }
            missing_pretty = [pretty.get(k, k) for k in missing]

            field_list = ", ".join(missing_pretty[:-1])
            if len(missing_pretty) > 1:
                field_list += f" and {missing_pretty[-1]}"
            else:
                field_list = missing_pretty[0]

            return (
                f"⚠️ I couldn't get all the necessary details to book your appointment.\n\n"
                f"Please rewrite your message including **{field_list}**.\n\n"
                "For example: `Book a doctor appointment tomorrow from 3pm to 4pm for stomach ache.`"
            )

        # Extra key checks before using params fields
        for k in required:
            if k not in params or not params[k] or params[k] == 'MISSING':
                return (
                    f"Sorry, the '{k}' field is missing or invalid.\n"
                    f"Extracted parameters: {params}\n"
                    f"Raw Gemini output: {raw_gemini}\n"
                    "Please try rephrasing your request or provide more details."
                )
        # Compose datetime strings in Asia/Kolkata
        from datetime import datetime
        from dateutil import tz
        try:
            ist = tz.gettz('Asia/Kolkata')
            start_dt = datetime.strptime(params['date'] + ' ' + params['start_time'], '%Y-%m-%d %H:%M').replace(tzinfo=ist)
            end_dt = datetime.strptime(params['date'] + ' ' + params['end_time'], '%Y-%m-%d %H:%M').replace(tzinfo=ist)
            start_str = start_dt.strftime('%Y-%m-%dT%H:%M:%S')
            end_str = end_dt.strftime('%Y-%m-%dT%H:%M:%S')
        except Exception as dt_err:
            return (
                f"Sorry, there was an error parsing the date or time.\n"
                f"Extracted parameters: {params}\n"
                f"Raw Gemini output: {raw_gemini}\n"
                f"Error: {dt_err}"
            )
        timezone = 'Asia/Kolkata'
        # Check availability and book
        try:
            is_free, busy_info = check_availability(start_str, end_str, timezone)
            if not is_free:
                return (
                    "❌ **Sorry, the time slot is already booked.**\n\n"
                    f"**Busy from:** {busy_info[0]['start'][-8:]} to {busy_info[0]['end'][-8:]} on {params['date']} (Asia/Kolkata timezone)\n"
                    f"**Your request:** {params['summary']} on {params['date']} from {params['start_time']} to {params['end_time']}\n\n"
                    "👉 Please try a different time or rewrite your message with a new slot."
                )
            event = create_event(start_str, end_str, params['summary'], params.get('description', ''), timezone)
            if isinstance(event, dict) and event.get("htmlLink"):
                return (
                    "✅ **Success! Your event has been booked.**\n\n"
                    f"**Summary:** {params['summary']}\n"
                    f"**Date:** {params['date']}\n"
                    f"**Time:** {params['start_time']} – {params['end_time']} (Asia/Kolkata)\n"
                    f"**Description:** {params.get('description', '') or 'No description'}\n\n"
                    f"[🗓️ Add to Calendar]({event['htmlLink']})"
                )
            else:
                return f"Sorry, there was an error booking your event.\nExtracted parameters: {params}\nRaw Gemini output: {raw_gemini}"
        except Exception as api_err:
            return (
                f"Sorry, something went wrong during booking.\n"
                f"Extracted parameters: {params}\n"
                f"Raw Gemini output: {raw_gemini}\n"
                f"Error: {api_err}"
            )
    except Exception as e:
        print(f"[Agent] Exception: {e}")
        import traceback
        traceback.print_exc()
        return (
            f"Sorry, something went wrong.\nError: {e}\n"
            f"Extracted parameters: {params}\n"
            f"Raw Gemini output: {raw_gemini}"
        )

# Example usage (for testing)
if __name__ == "__main__":
    print("Type your message (e.g., 'Book a meeting tomorrow at 3pm for 30 minutes'):")
    user_message = input()
    reply = run_agent_conversation(user_message)
    print("Agent:", reply)
