import asyncpraw
import asyncio
import disnake
import configparser
from disnake.ext import commands

# Loads up the configparser to read our login file
config = configparser.ConfigParser()
config.read('config')

# Creating a commands.Bot() instance and using 'bot'
bot = commands.Bot()

def reddit_auth():
    # Sets up the login for Reddit
    r = asyncpraw.Reddit(username=config['LOGIN']['username'],
                                   password=config['LOGIN']['password'],
                                   client_id=config['LOGIN']['client_id'],
                                   client_secret=config['LOGIN']['client_secret'],
                                   user_agent=config['LOGIN']['user_agent'])
    return r

reddit = reddit_auth()  # Authenticate to Reddit using Shturman creds.

# Setup allowed mentions by Discord bot
disnake.AllowedMentions(everyone=True, users=True, roles=True, replied_user=True)

guilds = [1079964891668021258, 937647740270280734]  # EFT Server, Test server

startup_time = datetime.datetime.now()


@bot.event  # Bot has launched and is ready.
async def on_ready():
    print("The bot is ready!")

    mqcd = 0  # Mod Queue counter
    umcd = 0  # Unmod Queue counter
    while True:
        try:
            mqcounter = 0
            umcounter = 0
            subreddit = await reddit.subreddit("EscapefromTarkov")  # Set our subreddit
            modmail = await subreddit.modmail.unread_count()
            async for item in subreddit.mod.modqueue(limit=None):  # Build our Mod Queue #s
                mqcounter += 1
            async for item in subreddit.mod.unmoderated(limit=None):  # Build our Unmoderated #s
                umcounter += 1
            mmcounter = modmail["new"]
            discordactivity = f"R:{mqcounter} Q:{umcounter} M:{mmcounter}"  # Update Discord status
            activity = disnake.Activity(name=discordactivity, type=disnake.ActivityType.watching)
            await bot.change_presence(activity=activity)
        except:
            print(f'Que watcher || Trying again in 30s')
            try:
                print('Loss of connectivity to discord, sleeping for 30s and trying again')
                activity = disnake.Activity(name="connection to Reddit", type=disnake.ActivityType.watching)
                await bot.change_presence(activity=activity)
            except:
                await asyncio.sleep(30)
        await asyncio.sleep(30)


@bot.slash_command(guild_ids=guilds)
async def uptime(inter):
    uptime_stamp = datetime.datetime.now()
    difference = uptime_stamp - startup_time

    # Extract the days, seconds, and microseconds from the time difference
    total_seconds = difference.total_seconds()
    days = divmod(total_seconds, 86400)[0]  # 1 day = 86400 seconds
    seconds = total_seconds % 86400
    # Convert the remaining seconds to hours, minutes, and seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    calc_uptime = f"{int(days)} days, {int(hours)} hours, {int(minutes)} minutes, {seconds} seconds"

    await inter.send(f'Hello {inter.author.mention}, I\'ve been running for: {calc_uptime}')


bot.run(config['DISCORD']['token'])  # Authenticate to Discord via our local token
