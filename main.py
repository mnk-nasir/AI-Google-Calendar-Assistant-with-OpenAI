#!/usr/bin/env python3
"""
Google Calendar AI Agent (Python v2)
------------------------------------
Reimplementation of the n8n workflow:
"AI Agent : Google Calendar Assistant using OpenAI"

Features:
- Conversational assistant that handles scheduling requests.
- Can create or retrieve events using Google Calendar API.
- Understands natural language prompts like:
    "Add a meeting with Sarah next Monday 2pm"
    "Show me my events tomorrow"
- Automatically switches to MOCK mode when no API keys are found.
"""

import os
import logging
from datetime import datetime, timedelta
import requests
from openai import OpenAI
from config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("calendar_ai_agent")
cfg = Config.load_from_env()


# ---------- MOCK MODE HELPERS ----------
def mock_create_event(title, desc, start, end):
    log.info(f"[MOCK] Creating event '{title}' from {start} to {end}")
    return {"status": "mocked", "htmlLink": "https://calendar.google.com/mock/event"}

def mock_get_events(start, end):
    log.info(f"[MOCK] Retrieving events between {start} and {end}")
    return [
        {"summary": "Mock Meeting with Team", "start": start, "end": end},
        {"summary": "Demo Call", "start": start, "end": end},
    ]


# ---------- GOOGLE CALENDAR API ----------
def create_event(title: str, description: str, start_time: str, end_time: str):
    if cfg.mock:
        return mock_create_event(title, description, start_time, end_time)

    url = f"https://www.googleapis.com/calendar/v3/calendars/{cfg.CALENDAR_ID}/events"
    headers = {
        "Authorization": f"Bearer {cfg.GOOGLE_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start_time, "timeZone": cfg.TIMEZONE},
        "end": {"dateTime": end_time, "timeZone": cfg.TIMEZONE},
    }
    r = requests.post(url, headers=headers, json=payload)
    if not r.ok:
        raise Exception(f"Google Calendar API error: {r.text}")
    return r.json()


def get_events(start_time: str, end_time: str):
    if cfg.mock:
        return mock_get_events(start_time, end_time)

    url = f"https://www.googleapis.com/calendar/v3/calendars/{cfg.CALENDAR_ID}/events"
    headers = {"Authorization": f"Bearer {cfg.GOOGLE_API_TOKEN}"}
    params = {"timeMin": start_time, "timeMax": end_time, "singleEvents": True, "orderBy": "startTime"}
    r = requests.get(url, headers=headers, params=params)
    if not r.ok:
        raise Exception(f"Failed to retrieve events: {r.text}")
    return r.json().get("items", [])


# ---------- OPENAI PARSING ----------
def interpret_user_request(message: str):
    """
    Send user message to OpenAI to determine action (create/retrieve),
    and extract structured event details.
    """
    if cfg.mock:
        log.info("[MOCK] Interpreting user message via OpenAI")
        if "create" in message.lower() or "add" in message.lower():
            return {
                "action": "create",
                "event_title": "Team Meeting",
                "event_description": "Discuss ongoing projects",
                "start_date": (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=1, hours=11)).isoformat(),
            }
        return {
            "action": "get",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=1)).isoformat(),
        }

    client = OpenAI(api_key=cfg.OPENAI_API_KEY)
    system_prompt = (
        "You are a Google Calendar assistant. "
        "Analyze the user's message and return a JSON with keys: "
        "action ('create' or 'get'), event_title, event_description, start_date, end_date. "
        "Date format: ISO8601. If retrieving, include start_date and end_date range."
    )
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
        temperature=0.2,
    )
    import json, re
    text = res.choices[0].message.content
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"(\{.*\})", text, re.S)
        return json.loads(m.group(1)) if m else {}


# ---------- MAIN WORKFLOW ----------
def run_agent(user_message: str):
    log.info(f"🤖 Received message: {user_message}")
    data = interpret_user_request(user_message)
    action = data.get("action")

    if action == "create":
        title = data.get("event_title") or "Untitled Event"
        desc = data.get("event_description", "")
        start = data.get("start_date")
        end = data.get("end_date")
        result = create_event(title, desc, start, end)
        return f"✅ Event '{title}' created successfully!\n{result.get('htmlLink')}"

    elif action == "get":
        start = data.get("start_date")
        end = data.get("end_date")
        events = get_events(start, end)
        if not events:
            return "No events found in that range."
        reply = "📅 Here are your events:\n"
        for e in events:
            reply += f"- {e.get('summary', 'Untitled')} ({e.get('start', {}).get('dateTime', start)})\n"
        return reply

    else:
        return "Hello! I can help you manage your Google Calendar — ask me to create or check events."


def main():
    import sys
    user_input = " ".join(sys.argv[1:]) or "Create a meeting with Alex tomorrow at 2 PM"
    reply = run_agent(user_input)
    print(reply)


if __name__ == "__main__":
    main()
