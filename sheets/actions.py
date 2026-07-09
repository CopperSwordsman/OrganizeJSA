from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import config

# --- HEADERS ---
REMINDER_HEADERS = ['Reminder_ID','Reminder_Timestamp','Channel_ID','Message','Days_In_Advance']

#HELPERS
def parseMonth(isostring):
    dt_object = datetime.fromisoformat(isostring)
    formatted_date = dt_object.strftime("%m/%d")
    return formatted_date

#REMINDER STUFF
def log_reminder(client, master_sheet_id, channel, message, time, people_to_ping,days_in_advance):
    #this is just for adding 1 to the year in case we're doing something between december and january I guess
    now = datetime.now()
    now = now.replace(hour=0,minute=0,second=0,microsecond=0)
    isotime=datetime.strptime(time,"%m/%d")
    isotime = isotime.replace(year=now.year)
    if(isotime<now):
        isotime = isotime.replace(year = now.year + 1)
    isotime = isotime.astimezone(tz=ZoneInfo("America/New_York")).isoformat()

    #logging the reminder itself
    master_wb = client.open_by_key(master_sheet_id)
    event_reminders = master_wb.worksheet("Board_Reminders")
    id_column = event_reminders.col_values(1)
    last_id = id_column[-1]
    try:
        last_id = int(last_id)
    except ValueError:
        last_id=0
    event_reminders.append_row([last_id+1,people_to_ping,isotime,channel,message,days_in_advance,"Scheduled"])
    return last_id+1
def get_reminders(client,master_sheet_id,expectedTime):
    #Reminder Statuses
    #Scheduled: Available to be reminded on when needed (usually day of)
    #Refresh: These are for when reminders need to be sent multiple times, it's already been sent today so we pend it to tomorrow
    #Cancelled: Scheduled but cancelled the day before
    #Expired: Day has passed

    sheet = client.open_by_key(master_sheet_id)
    board_reminders = sheet.worksheet("Board_Reminders")
    records = board_reminders.get_all_records(expected_headers=REMINDER_HEADERS)
    for index, row in enumerate(records):
        status=str(row.get("Status"))
        rowStartTime = str(row.get("Reminder_Timestamp"))
        rowStartTime = datetime.fromisoformat(rowStartTime)
        #First is to set all to expired just in case, I don't think this actually matters unless it was cancelled but consistency is nice
        if(expectedTime>rowStartTime):
            board_reminders.update_cell(index+2,7,'Expired')
        #If it's not scheduled it doesn't matter because we don't need to read it in that case
        if(status != "Scheduled"):
            continue

        daysInAdvance = int(row.get("Days_In_Advance"))
        rowID = str(row.get("Reminder_ID"))
        #In most cases we just need this if statement, if daysinadvance is anything but 1 though that changes
        if(expectedTime==rowStartTime):
            message = "# Time Until Deadline: 0 days\n" + "### " + str(row.get("Message") + "\n" + "ID: " + rowID)
            channel = str(row.get("Channel_ID"))
            pings = str(row.get("Pinged_Users"))
            board_reminders.update_cell(index+2,7,'Expired')
            return [message,channel,pings]
        #for higher days in advance we have to actually use refresh
        elif expectedTime < rowStartTime <= expectedTime + timedelta(days=daysInAdvance):
            #this is the case where we use days in advance, we don't want to change the status
            dayDifference = (rowStartTime-expectedTime).days
            message = f"# Time Until Deadline: {dayDifference} days\n" + "### " + str(row.get("Message") + "\n\n" + "ID: " + rowID)
            channel = str(row.get("Channel_ID"))
            pings = str(row.get("Pinged_Users"))
            board_reminders.update_cell(index+2,7,'Refresh')
            return [message,channel,pings]

    return None


def get_own_reminders(client,  master_sheet_id, userid, ismm):
    #this goes through discord ids to check if the id string is somewhere in the pinged user section, impossible for this to messup because of how discord is formatted
    #also could've made this use just roles but not all positions have roles on the discord, so just MM was made to have this feature, if people want it to change though that shouldn't be too difficult
    sheet = client.open_by_key(master_sheet_id)
    board_reminders = sheet.worksheet("Board_Reminders")
    mmrole = config.MULTIMEDIA_ROLE_ID
    records = board_reminders.get_all_records(expected_headers = REMINDER_HEADERS)
    reminderString = ""
    reminders = []
    for index, row in enumerate(records):
        status = str(row.get("Status"))
        id = str(row.get("Reminder_ID"))
        pingedusers = str(row.get("Pinged_Users"))
        #Cancelled could lowk be removed but we'll leave the cancelled and not expired the way it is
        #if user is pinged then we just check user
        #if user isn't pinged we can check if user has mm role and check for that
        if (status != "Cancelled" and status != "Expired") and ((str(userid) in pingedusers) or (ismm and str(mmrole) in pingedusers)):
            duedate = parseMonth(str(row.get("Reminder_Timestamp")))
            message = str(row.get("Message"))
            #we really need a simpler way to convert reminder time to readable stuff lol
            reminderString += ("Due Date: **" + duedate + "**\n")
            reminderString += pingedusers +"\n"
            reminderString += (message + "\n")
            reminderString += ("ID: " + id + "\n\n")
            reminders.append((duedate,reminderString))
            reminderString = ""
    #this is just to sort based on date, we logically want earlier dates to be sorted at the top, later ones at the bottom
    sorted_reminders = sorted(reminders, key = lambda item: (datetime.strptime(item[0],"%m/%d"),item[1]))
    for date,text in sorted_reminders:
        reminderString += text
    return reminderString


def reset_sent_reminders(client,master_sheet_id):
    #Converts refresh to scheduled that's literally it
    sheet = client.open_by_key(master_sheet_id)
    board_reminders = sheet.worksheet("Board_Reminders")
    records = board_reminders.get_all_records(expected_headers=REMINDER_HEADERS)
    for index, row in enumerate(records):
        status = str(row.get("Status"))
        if(status == "Refresh"):
            board_reminders.update_cell(index+2,7,'Scheduled')
def cancel_reminder_by_id(client,master_sheet_id,id):
    #This just cancels
    sheet = client.open_by_key(master_sheet_id)
    event_reminders=sheet.worksheet("Board_Reminders")
    records=event_reminders.get_all_records(expected_headers=REMINDER_HEADERS)
    numcleared = 0
    for index, row in enumerate(records):
        status = str(row.get("Status"))
        if(status != "Scheduled" and status != "Refresh"):
            continue
        try:
            row_id = int(row.get("Reminder_ID"))
            if(row_id == id):
                numcleared +=1
                event_reminders.update_cell(index+2,7,'Cancelled')
        except:
            continue
    return numcleared