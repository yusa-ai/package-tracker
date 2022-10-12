# package-tracker

A *"Fine, I'll do it myself"* Python script to track the status of my package from a certain website and send any update to my phone as a push notification.

## Context

I ordered a certain item from a certain website and the shipping service used for my package doesn't provide any way of receiving status updates, be it by email or by text message.  
That's where this handy, little script comes into play.  

## How it works

This Python script uses web scraping to:  
- Load the package tracking webpage
- Read the lastest status update provided
- Compare it against the last stored status message and send a push notification if there is something new

![Package status](https://i.imgur.com/UdsVRCk.png)

![Pushover notification](https://i.imgur.com/g3Y5qKK.jpg)

## Dependencies

| Package    | Version | Description                                           |
|------------|---------|-------------------------------------------------------|
| `requests` | 2.28.1  | Sending push notifications using Pushover's API       |
| `selenium` | 4.5.0   | Web scraping                                          |
| `gspread`  | 5.5.0   | Storing the latest package update using Google Sheets |

## Usage

You might want to clone this repository and edit the relevant sections of the script about scraping the status update in HTML before deploying the project to Heroku.

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Additionally, every environment variable (aside from `GOOGLE_CHROME_BIN` and `CHROMEDRIVER_PATH` if deploying to Heroku) should be set according to your settings and needs.  

Of course, this script can also be ran on a personal machine with an appropriate web driver installed and the relevant environment variables set.

As such, you will need:
- A Pushover user account and app (free 30-day trial available as of 10/12/2022)
- A Google Cloud project linked to your Google Sheet (see [gspread documentation](https://docs.gspread.org/en/latest/oauth2.html))

> **Note**: The script will read and write the latest status update of your package in worksheet 0, cell A1. This *can* be changed.

## License

[MIT](https://raw.githubusercontent.com/yusa-ai/package-tracker/main/LICENSE)
