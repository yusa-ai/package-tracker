import os

import gspread
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


TRACKING_URL = os.environ.get("TRACKING_URL")

# Google Sheets
GOOGLE_CREDENTIALS = {
  "type": "service_account",
  "project_id": os.environ.get("GOOGLE_PROJECT_ID"),
  "private_key_id": os.environ.get("GOOGLE_PRIVATE_KEY_ID"),
  "private_key": os.environ.get("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
  "client_email": os.environ.get("GOOGLE_CLIENT_EMAIL"),
  "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": os.environ.get("GOOGLE_CLIENT_X509_CERT_URL")
}
GOOGLE_SPREADSHEET_NAME = "package-tracker"

# Pushover
PUSHOVER_APP_TOKEN = os.environ.get("APP_TOKEN")
PUSHOVER_USER_KEY = os.environ.get("USER_KEY")


options = Options()
options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
options.headless = True
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))

driver = webdriver.Chrome(options=options, service=service)


driver.get(TRACKING_URL)

page_loaded = False

# Wait for page loading
while not page_loaded:
    try:
        driver.find_element(By.CSS_SELECTOR, ".el-loading-mask")

    except NoSuchElementException:
        page_loaded = True

# driver.get_screenshot_as_file("screenshot.png")

# Get last tracking status
timeline = driver.find_elements(By.CSS_SELECTOR, ".timeline-main.clearfix")

timeline = [item for item in timeline if item.text != ""]
last_update = timeline[0].text
last_update = last_update.replace("\n", " ")

# Initialize Google Spreadsheet
gc = gspread.service_account_from_dict(GOOGLE_CREDENTIALS)
sh = gc.open(GOOGLE_SPREADSHEET_NAME)
worksheet = sh.get_worksheet(0)

# Read last status from Google Sheets
saved_status = worksheet.acell("A1").value

if last_update != saved_status:
    # Update Google Sheets
    worksheet.update("A1", last_update)

    # Send push notification
    result = requests.post("https://api.pushover.net/1/messages.json", json={
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": last_update
    })
    result.raise_for_status()
    print(f"[PackageTracker] Notification sent: {last_update}")

else:
    print(f"[PackageTracker] Package status up to date")
