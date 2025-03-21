import os
import requests
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

# 載入環境變數
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
    """ 從 Notion 讀取事件 """
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=NOTION_HEADERS)

    if response.status_code != 200:
        print("無法取得 Notion 事件，請檢查 API Key 和資料庫權限")
        return []

    events = response.json().get("results", [])
    notion_events = []

    for event in events:
        properties = event["properties"]

        # 自動偵測標題欄位
        title_key = next(key for key in properties if properties[key]["type"] == "title")
        title = properties[title_key]["title"][0]["text"]["content"] if properties[title_key]["title"] else "無標題"

        # 取得開始時間 & 結束時間
        start_date = properties["Date"]["date"]["start"] if "Date" in properties and properties["Date"]["date"] else None
        end_date = properties["Date"]["date"]["end"] if "Date" in properties and properties["Date"]["date"] else None

        # 取得 Status（如果有）
        status = properties["Status"]["select"]["name"] if "Status" in properties and properties["Status"]["select"] else None

        # 如果 Status 是 Done，就跳過同步
        if status and status.lower() == "done":
            print(f"跳過已完成事件: {title}")
            continue

        # 取得 Notes（如果有）
        notes = properties["Notes"]["rich_text"][0]["text"]["content"] if "Notes" in properties and properties["Notes"]["rich_text"] else ""

        # 判斷是否為全天事件
        is_all_day = "T" not in start_date if start_date else True

        # 如果只有 start，沒有 end，則設定為 start + 1 小時
        if start_date and not end_date and not is_all_day:
            start_dt = datetime.datetime.fromisoformat(start_date)
            end_dt = start_dt + datetime.timedelta(hours=1)
            end_date = end_dt.isoformat()

        if start_date:
            notion_events.append({
                "title": title,
                "start_date": start_date,
                "end_date": end_date,
                "description": notes,
                "is_all_day": is_all_day,
            })

    print(f"從 Notion 讀取 {len(notion_events)} 個事件")
    return notion_events

def get_google_calendar_service():
    """ 連接 Google Calendar API """
    credentials = service_account.Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=["https://www.googleapis.com/auth/calendar"])
    return build("calendar", "v3", credentials=credentials)

def get_existing_google_events(service):
    """ 取得 Google Calendar 內所有事件標題，避免重複新增 """
    events_result = service.events().list(
        calendarId=GOOGLE_CALENDAR_ID,
        timeMin=datetime.datetime.utcnow().isoformat() + "Z",
        maxResults=100,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    existing_titles = {event["summary"] for event in events_result.get("items", [])}
    print(f"Google Calendar 內已有 {len(existing_titles)} 個事件")
    return existing_titles

def add_event_to_google_calendar(event, existing_titles):
    """ 將 Notion 事件同步到 Google Calendar，避免重複 """
    service = get_google_calendar_service()

    # 檢查標題是否已存在於 Google Calendar
    if event["title"] in existing_titles:
        print(f"事件已存在，不重複新增: {event['title']}")
        return

    google_event = {
        "summary": event["title"],
        "description": event["description"],
    }

    # 根據是否是全天事件決定時間格式
    if event["is_all_day"]:
        google_event["start"] = {"date": event["start_date"]}
        google_event["end"] = {"date": event["end_date"] if event["end_date"] else event["start_date"]}
    else:
        google_event["start"] = {"dateTime": event["start_date"], "timeZone": "Asia/Taipei"}
        google_event["end"] = {"dateTime": event["end_date"] if event["end_date"] else event["start_date"], "timeZone": "Asia/Taipei"}

    created_event = service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=google_event).execute()
    print(f"已同步至 Google Calendar: {event['title']}")

def sync_notion_to_google_calendar():
    """ 執行 Notion → Google Calendar 同步 """
    notion_events = get_notion_events()
    if not notion_events:
        print("沒有需要同步的 Notion 事件")
        return

    service = get_google_calendar_service()
    existing_titles = get_existing_google_events(service)

    for event in notion_events:
        add_event_to_google_calendar(event, existing_titles)

    print("Notion → Google Calendar 同步完成")

# 執行同步
sync_notion_to_google_calendar()
