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

guilds = [937647740270280734]  # Test server
#guilds = [1079964891668021258]  # EFT server


def embeder(description):  # Function to allow us to easily build embeded messages with a default look.
    embed = disnake.Embed(
        title="Usable commands",
        description=description,
        color=disnake.Colour.yellow(),
        timestamp=datetime.datetime.now(),
    )
    embed.set_author(
        name="ShturmanBOT",
        url="https://github.com/Jimloe",
        icon_url="https://i.imgur.com/OcjbuK1.jpg"  # Shturmans face
    )
    embed.set_footer(
        text="Created by Jimlo#4389",
        icon_url="https://i.imgur.com/SGRBBDo.jpg"  # Jimlos Avatar
    )
    embed.set_thumbnail(url="https://i.imgur.com/bkzBSgY.png?1")  # EFT Snoo Thumbnail
    # embed.set_image(url="https://i.imgur.com/p51DB4k.jpg")  # Use this if you want a large footer image.
    return embed


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
async def rules(inter):
    await inter.response.send_message(
        f'Hello {inter.author.mention}!',
        components=[
            disnake.ui.Button(label="R1", style=disnake.ButtonStyle.primary, custom_id="R1"),
            disnake.ui.Button(label="R2", style=disnake.ButtonStyle.secondary, custom_id="R2"),
            disnake.ui.Button(label="R3", style=disnake.ButtonStyle.success, custom_id="R3"),
            disnake.ui.Button(label="R4", style=disnake.ButtonStyle.danger, custom_id="R4"),
            disnake.ui.Button(label="R5", style=disnake.ButtonStyle.primary, custom_id="R5"),
            disnake.ui.Button(label="R6", style=disnake.ButtonStyle.secondary, custom_id="R6"),
            disnake.ui.Button(label="R7", style=disnake.ButtonStyle.success, custom_id="R7"),
            disnake.ui.Button(label="R8", style=disnake.ButtonStyle.danger, custom_id="R8"),
        ],
    )

@bot.listen("on_button_click")
async def help_listener(inter: disnake.MessageInteraction):
    if inter.component.custom_id not in ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]:
        # We filter out any other button presses except
        # the components we wish to process.
        return

    if inter.component.custom_id == "R1":
        await inter.response.send_message("You hit R1, yay!")
    elif inter.component.custom_id == "R2":
        await inter.response.send_message("You hit R2, yay!")
    elif inter.component.custom_id == "R3":
        await inter.response.send_message("You hit R3, yay!")
    elif inter.component.custom_id == "R4":
        await inter.response.send_message("You hit R4, yay!")
    elif inter.component.custom_id == "R5":
        await inter.response.send_message("You hit R5, yay!")
    elif inter.component.custom_id == "R6":
        await inter.response.send_message("You hit R6, yay!")
    elif inter.component.custom_id == "R7":
        await inter.response.send_message("You hit R7, yay!")
    elif inter.component.custom_id == "R8":
        await inter.response.send_message("You hit R8, yay!")



bot.run(config['DISCORD']['token'])  # Authenticate to Discord via our local token
