# AI-Google-Calendar-Assistant-with-OpenAI# 📅 Google Calendar AI Agent (Python v2)

Recreated from your n8n workflow:
**“AI Agent : Google Calendar Assistant using OpenAI”**

---

## 🧩 Features
- Understands natural language to **create** or **fetch** Google Calendar events  
- Uses **OpenAI GPT** for intent detection & entity extraction  
- Works in **mock mode** with no API keys  
- Can be expanded to handle attendees, reminders, or cancellations  

---

## 🚀 Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
Add your API keys to .env (or leave blank to test mock mode).

▶️ Run
bash
Copy code
python calendar_ai_agent.py "Create meeting with John tomorrow at 3 PM"
Example output:

bash
Copy code
✅ Event 'Meeting with John' created successfully!
https://calendar.google.com/mock/event
or:

bash
Copy code
python calendar_ai_agent.py "Show me my meetings for next week"
🧠 How it Works
Interpret user intent via GPT

Extract structured fields (title, description, start_date, end_date)

Call Google Calendar API for event creation or retrieval

Reply with natural-language confirmation

🧩 Extend It
Add attendee support

Integrate recurring events

Add Telegram or Discord bot interface

Deploy via GitHub Actions for periodic reminders
