import discord
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands
import asyncio
import config
from sheets.client import get_client
from sheets import actions
from zoneinfo import ZoneInfo
import datetime

intents = discord.Intents.default()
intents.message_content = True
GUILD_ID = discord.Object(id = config.GUILD_ID)
class Client(commands.Bot):
    async def on_ready(self):
        print(f"Logged in as {self.user}")
        print("Bot is ready to process sheets!")

        if not reminder_announcement_loop.is_running():
            reminder_announcement_loop.start()
bot = Client(command_prefix = "!", intents =intents)


@tasks.loop(minutes=10)
async def reminder_announcement_loop():
    client = get_client()
    currentDateTime = datetime.datetime.now(tz=ZoneInfo('America/New_York'))
    if(currentDateTime.hour < 10):
        #this is actually a spot we can correct the pending ones
        #but we also don't want to alert people too early in the morning
        actions.reset_sent_reminders(client,config.SHEET_ID)
        #Makes the wait time an hour which is fine, we don't need the loop to be doing anything for this time
        #Only reason it isn't 10 hours would be because it could trigger at 9:59 meaning reminders come in wayyyy later
        await asyncio.sleep(3600)
        return
    currentDateTime = currentDateTime.replace(hour=0,minute=0,second=0,microsecond=0)
    result = actions.get_reminders(client,config.SHEET_ID,currentDateTime)
    if(result != None):
        message = result[0]
        channel = result[1]
        pings = result[2]
        channel = int(channel.strip('<#>'))
        channelToSend = bot.get_channel(channel)
        my_embed = discord.Embed(title="Reminder ",
                                            description=message)

        await channelToSend.send(pings,embed = my_embed)
class ReminderModal(discord.ui.Modal,title='Event Message'):
    message_input = discord.ui.TextInput(
        label='Reminder',
        style=discord.TextStyle.paragraph,
        placeholder='paste reminder here',
        required=True

    )
    def __init__(self,_date,_channel,_pingedusers, _daysinadvance):
        super().__init__()
        self.pingedusers = _pingedusers
        self.date = _date
        self.channel = _channel
        self.daysinadvance = _daysinadvance

    async def on_submit(self,interaction:discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_message = self.message_input.value
        client = get_client()
        announcementid = actions.log_reminder(client,config.SHEET_ID,self.channel,user_message,self.date,self.pingedusers, self.daysinadvance)
        await interaction.followup.send_message(f"Scheduled announcement with id {announcementid}.", ephemeral=True)
@bot.tree.command(name = "schedule_request", description="Set a reminder, the reminder will ping whoever's included",guild=GUILD_ID)
@app_commands.describe(
    date="MM/DD"
)
@app_commands.checks.has_role(config.OFFICER_ROLE_ID)
async def schedule_board_reminder(interaction:discord.Interaction,pinged_users: str,date: str, channel: str,days_in_advance: int = 0):
    #client = get_client()
    await interaction.response.send_modal(ReminderModal(date,channel, pinged_users,days_in_advance))
@bot.tree.command(name = "cancel_request",description="Cancel an event that has been scheduled.",guild=GUILD_ID)
@app_commands.checks.has_role(config.OFFICER_ROLE_ID)
async def cancel_board_reminder(interaction:discord.Interaction,id: int):
    client = get_client()
    numcancelled = actions.cancel_reminder_by_id(client,config.SHEET_ID,id)
    await interaction.response.send_message(f"{numcancelled} events were cancelled.")
@bot.tree.command(name = "check_reminders", description="Check your own pending reminders.", guild = GUILD_ID)
#@app_commands.checks.has_role(config.OFFICER_ROLE_ID)
async def check_reminders(interaction:discord.Interaction):
    #here we mainly want to use the bot to check every reminder that has the user's id here
    #we can check if someone has certain roles that we would want to include in the ping check as well
    client = get_client()
    ismm = any(role.id == config.OFFICER_ROLE_ID for role in interaction.user.roles)
    reminderString = actions.get_own_reminders(client, config.SHEET_ID,interaction.user.id,ismm)
    reminderString = reminderString
    my_embed = discord.Embed(title="Reminders",description = reminderString)
    await interaction.response.send_message(ephemeral=True, embed=my_embed)

bot.run(config.DISCORD_TOKEN)