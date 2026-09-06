# Organize JSA
Made to add a request system to help people keep track of what they need to do
## How It Works
* `/schedule_board_reminder`: Makes a reminder, ping any users who need a reminder at a date and time in MM/DD format, and input a channel for the reminder to be sent if the date is reached. A reminder will be assigned to this date with an id.
* `/cancel_event_reminder`: Input the id of whatever reminder needs to be used
* `/check_reminders`: Use the command to see all reminders attributed to you

## Getting Started
### Prerequisites
* Python 3.8+
* Discord Bot Token [(Discord Developer Portal)](https://discord.com/developers/applications)
* Google Cloud Service Account with Sheets API enabled
* Google Sheets set up with required worksheets

### Installation
1. Clone the repository:
   
    ```bash
   git clone https://github.com/YOUR_USERNAME/Organize_JSA.git
   cd Organize_JSA
   ```
  
2. Create and activate a virtual environment:
   
   ```bash
   python -m venv venv
   source venv/bin/activate #On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   
   ```bash
   pip install -r requirements.txt
   ```
   
4. Set up environment variables:

   Create a `.env` file in the root directory:

   ```env
   DISCORD_TOKENN=your_discord_bot_token
   GOOGLE_SHEET_ID=your_google_sheet_id
   GUILD_NUM = your_discord_server_id
5. Add your Google Cloud service account credentials as `credentials.json` in the root directory.

6. Set up your Google Sheet with these worksheets:

   | Worksheet | Purpose |
   |-----------|---------|
   | `Board_Reminders` | (Reminder_ID, Pinged_Users, Reminder_Timestamp, Message, Days_In_Advance, Status) |

7. Run the bot:
   ```bash
   python bot.py
   ```

## Project Structure
```Organize_JSA/
├── bot.py                # Main Discord bot: commands, reminder loops
├── config.py             # Configuration and environment variables
├── requirements.txt      # Python dependencies
├── credentials.json      # Google Cloud service account (not in repo)
├── .env                  # Environment variables (not in repo)
├── sheets/
│   ├── client.py         # Google Sheets authentication (get_client)
│   └── actions.py        # Sheet operations (see below)
```
