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
import re

intents = discord.Intents.default()
intents.message_content = True
intents.members=True
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
    await actions.get_reminders(client, bot,config.SHEET_ID,currentDateTime)
class ReminderModal(discord.ui.Modal,title='Request Message'):
    message_input = discord.ui.TextInput(
        label='Reminder',
        style=discord.TextStyle.paragraph,
        placeholder='paste reminder here',
        required=True

    )
    def __init__(self,_date,_pingedusers, _requester):
        super().__init__()
        self.pingedusers = _pingedusers
        self.date = _date
        self.requester = _requester

    async def on_submit(self,interaction:discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_message = self.message_input.value
        client = get_client()
        user_ids = set(int(uid) for uid in re.findall(r"<@(\d+)>", self.pingedusers))
        role_ids = re.findall(r"<@&(\d+)>", self.pingedusers)
        for role_id in role_ids:
            role = interaction.guild.get_role(int(role_id))
            if role:
                user_ids.update(int(member.id) for member in role.members)

        requesterid = "<@" + str(self.requester.id) + ">"

        announcementid = actions.log_reminder(client,config.SHEET_ID,requesterid,user_message,self.date,self.pingedusers)
        for uid in user_ids:
            finalmessage = f"# Deadline: {self.date}\n" + "### " + str(user_message + "\n\n" + "ID: " +str(announcementid))
            my_embed = discord.Embed(title="Reminder ",
                                            description=finalmessage)
            try:
                user = await interaction.client.fetch_user(int(uid))
                await user.send(embed = my_embed)
            except (discord.Forbidden,discord.NotFound):
                print(f"Failed to DM, user has DMS disabled, blocked bot, or ID is invalid")
            except discord.HTTPException as e:
                print(f"Failed to DM {uid}: {e}")




        await interaction.followup.send(f"Scheduled announcement with id {announcementid}.", ephemeral=True)
@bot.tree.command(name = "schedule_board_reminder", description="Set a reminder, the reminder will ping whoever's included",guild=GUILD_ID)
@app_commands.describe(
    date="MM/DD"
)
@app_commands.checks.has_role(config.OFFICER_ROLE_ID)
async def schedule_board_reminder(interaction:discord.Interaction,pinged_users: str,date: str):
    #client = get_client()
    await interaction.response.send_modal(ReminderModal(date, pinged_users, interaction.user))
@bot.tree.command(name = "cancel_board_reminder",description="Cancel an event that has been scheduled.",guild=GUILD_ID)
@app_commands.checks.has_role(config.OFFICER_ROLE_ID)
async def cancel_board_reminder(interaction:discord.Interaction,id: int):
    client = get_client()
    numcancelled = actions.cancel_reminder_by_id(client,config.SHEET_ID,id)
    await interaction.response.send_message(f"{numcancelled} events were cancelled.")
@bot.tree.command(name = "check_reminders", description="Check your own pending reminders.", guild = GUILD_ID)
#@app_commands.checks.has_role(config.OFFICER_ROLE_ID)
async def check_reminders(interaction:discord.Interaction):
    #here we mainly want to use the bot to check every reminder that has the user's id here
    #we can check if someone has certain roles that we would want to include in the ping check as wella
    await interaction .response.defer(ephemeral=True)
    client = get_client()
    ismm = any(role.id == config.OFFICER_ROLE_ID for role in interaction.user.roles)
    reminderString = actions.get_own_reminders(client, config.SHEET_ID,interaction.user.id,ismm)
    reminderString = reminderString
    my_embed = discord.Embed(title="Reminders",description = reminderString)
    await interaction.followup.send(ephemeral=True, embed=my_embed)

bot.run(config.DISCORD_TOKEN)