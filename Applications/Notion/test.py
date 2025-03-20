import os
import requests
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("DATABASE_ID")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
GOOGLE_CREDENTIALS_FILE = "credentials.json"

if not NOTION_API_KEY or not DATABASE_ID or not GOOGLE_CALENDAR_ID:
    raise ValueError("環境變數未正確設置，請檢查 .env 檔案！")

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def get_notion_events():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=NOTION_HEADERS)

    if response.status_code == 200:
        events = response.json()["results"]
        notion_events = []

        for event in events:
            properties = event["properties"]

            title_key = next(key for key in properties if properties[key]["type"] == "title")

            title = properties[title_key]["title"][0]["text"]["content"] if properties[title_key]["title"] else "無標題"
            start_date = properties["Due date"]["date"]["start"] if "Due date" in properties and properties["Due date"]["date"] else None

            if start_date:
                notion_events.append({"title": title, "start_date": start_date, "notion_id": event["id"]})

        return notion_events
    else:
        print("無法取得 Notion 事件，請檢查 API Key 和資料庫權限")
        return []

def get_google_calendar_service():
    credentials = service_account.Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=["https://www.googleapis.com/auth/calendar"])
    return build("calendar", "v3", credentials=credentials)

def event_exists(service, event_title, start_date):
    events_result = service.events().list(
        calendarId=GOOGLE_CALENDAR_ID,
        q=event_title,
        timeMin=f"{start_date}T00:00:00Z",
        timeMax=f"{start_date}T23:59:59Z",
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    
    return len(events_result.get("items", [])) > 0

def add_event_to_google_calendar(event_title, start_date, time="all-day"):
    service = get_google_calendar_service()

    if event_exists(service, event_title, start_date):
        print(f"事件已存在，不重複新增: {event_title} ({start_date})")
        return

    event = {
        "summary": event_title,
        "start": {"date": start_date},
        "end": {"date": start_date},
    }

    if time == "specific":
        event["start"] = {"dateTime": f"{start_date}T10:00:00", "timeZone": "Asia/Taipei"}
        event["end"] = {"dateTime": f"{start_date}T11:00:00", "timeZone": "Asia/Taipei"}

    created_event = service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=event).execute()
    print(f"已新增至 Google Calendar: {event_title} ({created_event.get('htmlLink')})")

def sync_notion_to_google_calendar():
    notion_events = get_notion_events()
    if not notion_events:
        print("沒有需要同步的 Notion 事件")
        return

    for event in notion_events:
        add_event_to_google_calendar(event["title"], event["start_date"])

sync_notion_to_google_calendar()
