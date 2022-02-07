import asyncio
import configparser
import datetime
import disnake
import re
import logging
from reddit_helper import ShturReddit
from disnake.ext import commands
# from dropdown import DropdownView

# Invite URL BOT: https://discord.com/api/oauth2/authorize?client_id=721249120190332999&permissions=328565075008&scope=bot%20applications.commands
# Invite URL TestBOT: https://discord.com/api/oauth2/authorize?client_id=781571125716844614&permissions=397284599872&scope=bot%20applications.commands

# Logging configuration
logging.basicConfig(format='%(levelname)s-%(asctime)s-%(message)s', level=logging.DEBUG, datefmt='%Y%m%d:%H:%M:%S')

# Loads up the configparser to read our login file
config = configparser.ConfigParser()
config.read('config')

# Creating a commands.Bot() instance and using 'bot'
bot = commands.Bot()

# Setup allowed mentions by Discord bot
disnake.AllowedMentions(everyone=True, users=True, roles=True, replied_user=True)

guilds = config['DISCORD']['guilds']  # Import our config file of Discord servers
guilds = guilds.split(',')  # Split our text list into an actual list
guilds = [int(i) for i in guilds]  # Convert string list into int list


@bot.event  # Bot has launched and is ready.
async def on_ready():
    logging.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logging.info("The bot is ready!")


# @bot.event
# async def on_slash_command_error(inter, error):
#     print(f'Ran into an error:{error}')
#     await inter.send("I didn't understand your command")


@bot.event
async def on_disconnect(dc):
    logging.warning(f'Disconnected from Discord:{dc}')


@bot.event
async def on_resumed():
    logging.warning(f'Reconnected to discord!')


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


@bot.slash_command(guild_ids=guilds)
async def help_shturman(inter):
    embed = embeder("This lists out important commands!")
    embed.add_field(name="Regular Title", value="Regular Value", inline=False)
    embed.add_field(name="Inline Title", value="Inline Value", inline=True)
    embed.add_field(name="Inline Title", value="Inline Value", inline=True)
    embed.add_field(name="Inline Title", value="Inline Value", inline=True)
    await inter.response.send_message(embed=embed)


@bot.slash_command(guild_ids=guilds, description="Shturman will monitor the Mod queue numbers.")
async def watchque(inter, runprgm='enable', notify='true', counter=35):
    hello = ShturReddit.random_hello()
    modguild = bot.get_guild(int(config['DISCORD']['eftserver']))
    modmention = modguild.get_role(int(config['DISCORD']['modrole']))
    chanannounce = bot.get_channel(int(config['DISCORD']['eftannounce']))

    if runprgm == 'enable':
        if notify.lower() == "true":
            cd = 0

            await inter.send(f'{hello} {inter.author.mention}!, '
                             f'I\'ll monitor the mod queues, and notify when the queue hits {counter}')
            logging.info(f"{inter.author.mention} started watchque module with notifications.")
            while True:
                mqcounter, umcounter, mmcounter = await ShturReddit.queue_counter()

                activity = disnake.Activity(name=f"R:{mqcounter} Q:{umcounter} M:{mmcounter}",
                                            type=disnake.ActivityType.watching)
                await bot.change_presence(activity=activity)

                if (mqcounter >= counter or umcounter >= counter) and cd == 0:
                    await chanannounce.send(f"\n{modmention.mention}, please check the queues! "
                                            f"R:{mqcounter} Q:{umcounter} M:{mmcounter}")
                    cd += 1
                if cd == 120:  # There are 120 instances of 30s increments in an hour.
                    logging.info("Resetting notification counter")
                    cd = 0
                else:
                    cd += 1

                await asyncio.sleep(30)

        elif notify.lower() == "false":
            await inter.send(f'{hello} {inter.author.mention}!, '
                             f'I\'ll monitor the mod queues, and won\'t send notifications.')
            logging.info(f"{inter.author.mention} started watchque module. No notifications.")
            while True:
                mqcounter, umcounter, mmcounter = await ShturReddit.queue_counter()
                activity = disnake.Activity(name=f"R:{mqcounter} Q:{umcounter} M:{mmcounter}",
                                            type=disnake.ActivityType.watching)
                await bot.change_presence(activity=activity)
                await asyncio.sleep(30)
        else:
            await inter.send(f'{hello} {inter.author.mention}!, I didn\'t understand your syntax.')
            return


@bot.slash_command(guild_ids=guilds, description="Backup Sub config locally, images won't by saved by default.")
async def backup_eft(inter, images='false'):
    hello = ShturReddit.random_hello()

    await inter.send(f'{hello} {inter.author.mention}!, Backing up the configurations now....')
    logging.info(f"{inter.author.mention} started a backup job.")

    backupjob = await ShturReddit.backup_eft(images=images)

    if backupjob:
        logging.info(f"Backup job has been completed")
        await inter.followup.send(f'{hello} {inter.author.mention}!, Finished backing things up!')
    else:
        logging.warning("Backup job encountered an error.")
        await inter.followup.send(f'{hello} {inter.author.mention}!, I encountered an error!')


@bot.slash_command(guild_ids=guilds, description="Monitors subreddit for Dev posts and announces them in Discord.")
async def dev_tracker(inter):
    # Import and build the channel object for sending messages.
    announce = int(config['DISCORD']['eftannounce'])
    chanannounce = bot.get_channel(announce)

    hello = ShturReddit.random_hello()

    logging.info(f"{inter.author.mention} started the dev tracker module.")
    await inter.send(f'{hello} {inter.author.mention}!, I\'ll watch the sub for Dev posts & comments.')

    devtrack = await ShturReddit.devtracker(chanannounce)


@bot.slash_command(guild_ids=guilds, description="Monitors subreddit for R5 violations.")
async def rule5_enforcer(inter, action='report'):
    hello = ShturReddit.random_hello()
    
    logging.info(f"{inter.author.mention} started the Rule 5 enforcer module.")
    await inter.send(f'{hello} {inter.author.mention}!, I\'ll start enforcing Rule 5 on the sub.')

    rule5 = await ShturReddit.rule5_enforcer(action=action)


@bot.slash_command(guild_ids=guilds, description="Removes a post and sends a removal reason.")
async def remove_post(inter: disnake.CommandInteraction, reason=1, url='https://old.reddit.com/r/EscapefromTarkov/comments/siu874/test_remove_post/'):
    hello = ShturReddit.random_hello()

    logging.info(f"{inter.author.mention} is attempting to remove a post: Rule:{reason}, URL={url}")

    # await inter.send(f'{hello} {inter.author.mention}!, I\'ll start enforcing Rule 5 on the sub.')

    matcher = re.match('\w*://\w*.reddit.com/r/EscapefromTarkov/comments/', url)
    if not matcher:
        await inter.response.send_message(f'{inter.author.mention}, you\'ve sent me a fucked up link.')
        return
    try:
        intreason = int(reason)
    except:
        await inter.response.send_message(f'{inter.author.mention}, the reason you provided isn\'t an integer.')
        return

    removalreasons = await ShturReddit.removal_reasons(reason=reason, url=url, matcher=matcher)

    options = []
    selectmenu = disnake.ui.Select

    for reasontxt in removalreasons:
        reasontxt = reasontxt.strip()  # Strip off leading and trailing spaces
        optbuilder = f'"label={intreason}", description="{reasontxt}"'
        selectmenu.add_option(label=intreason, description=reasontxt)
        options.append(optbuilder)

    logging.DEBUG(f"Options: {options}")

    view = disnake.ui.View()
    view.add_item(MySelect())
    await inter.response.send_message("ORIGINAL", view=view)

    # view = disnake.ui.View
    # # # Create the view containing our dropdown
    # # view = DropdownView(options)
    # #
    # # # Sending a message containing our view
    # await inter.send("Pick a removal reason:", view=view)


class MySelect(disnake.ui.Select):

    def __init__(self):
        opts = [
            disnake.SelectOption(label=s)
            for s in "abc"
        ]
        super().__init__(options=opts)

    async def callback(self, inter: disnake.CommandInteraction):
        await inter.response.send_message("")


# IN COG:
@bot.slash_command(guild_ids=guilds)
async def select_test(self, inter: disnake.CommandInteraction):
    view = disnake.ui.View()
    view.add_item(MySelect())
    await inter.response.send_message("ORIGINAL", view=view)


bot.run(config['DISCORD']['token'])  # Authenticate to Discord via our local token