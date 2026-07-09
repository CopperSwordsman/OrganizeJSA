# Organize JSA
Made to add a request system to help people keep track of what they need to do
## How It Works
* `/schedule_board_reminder`: Makes a reminder, ping any users who need a reminder at a date and time in MM/DD format, and input a channel for the reminder to be sent if the date is reached. A reminder will be assigned to this date with an id.
* `/cancel_event_reminder`: Input the id of whatever reminder needs to be used
* `/check_reminders`: Use the command to see all reminders attributed to you
