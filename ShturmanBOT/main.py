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
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(message)s', datefmt='%Y%m%d:%H:%M:%S')
# file_handler = logging.FileHandler('logfile.log')
# file_handler.setLevel(logging.DEBUG)
# file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
# logger.addHandler(file_handler)
logger.addHandler(stream_handler)


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
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logger.info("The bot is ready!")


# @bot.event
# async def on_slash_command_error(inter, error):
#     print(f'Ran into an error:{error}')
#     await inter.send("I didn't understand your command")


@bot.event
async def on_disconnect(dc):
    logger.warning(f'Disconnected from Discord:{dc}')


@bot.event
async def on_resumed():
    logger.warning(f'Reconnected to discord!')


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
            logger.info(f"{inter.author.name} started watchque module with notifications.")
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
                    logger.info("Resetting notification counter")
                    cd = 0
                else:
                    cd += 1

                await asyncio.sleep(30)

        elif notify.lower() == "false":
            await inter.send(f'{hello} {inter.author.mention}!, '
                             f'I\'ll monitor the mod queues, and won\'t send notifications.')
            logger.info(f"{inter.author.name} started watchque module. No notifications.")
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
    logger.info(f"{inter.author.name} started a backup job.")

    backupjob = await ShturReddit.backup_eft(images=images)

    if backupjob:
        logger.info(f"Backup job has been completed")
        await inter.followup.send(f'{hello} {inter.author.mention}!, Finished backing things up!')
    else:
        logger.warning("Backup job encountered an error.")
        await inter.followup.send(f'{hello} {inter.author.mention}!, I encountered an error!')


@bot.slash_command(guild_ids=guilds, description="Monitors subreddit for Dev posts and announces them in Discord.")
async def dev_tracker(inter):
    # Import and build the channel object for sending messages.
    announce = int(config['DISCORD']['eftannounce'])
    chanannounce = bot.get_channel(announce)

    hello = ShturReddit.random_hello()

    logger.info(f"{inter.author.name} started the dev tracker module.")
    await inter.send(f'{hello} {inter.author.mention}!, I\'ll watch the sub for Dev posts & comments.')

    devtrack = await ShturReddit.devtracker(chanannounce)


@bot.slash_command(guild_ids=guilds, description="Monitors subreddit for R5 violations.")
async def rule5_enforcer(inter, action='report'):
    hello = ShturReddit.random_hello()
    
    logger.info(f"{inter.author.name} started the Rule 5 enforcer module.")
    await inter.send(f'{hello} {inter.author.mention}!, I\'ll start enforcing Rule 5 on the sub.')

    rule5 = await ShturReddit.rule5_enforcer(action=action)


@bot.slash_command(guild_ids=guilds, description="Removes a post and sends a removal reason.")
async def remove_post(inter: disnake.CommandInteraction, reason=2, url='https://old.reddit.com/r/EscapefromTarkov/comments/siu874/test_remove_post/'):
    logger.info(f"{inter.author.name} is attempting to remove a post: Rule:{reason}, URL={url}")

    hello = ShturReddit.random_hello()

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

    for reasontxt in removalreasons:
        reasontxt = reasontxt.strip()  # Strip off leading and trailing spaces
        optbuilder = {'label': intreason, 'description': reasontxt}
        options.append(optbuilder)

    logger.debug(f"Options: {options}")

    view = disnake.ui.View()
    view.add_item(MySelect(removals=options))
    await inter.response.send_message("Select a removal reason:", view=view)


class MySelect(disnake.ui.Select):

    fulldesc = []

    def __init__(self, removals):
        self.removals = removals

        opts = []
        value = 1
        for i in self.removals:
            selectopt = str(i['label'])
            description = str(i['description'])
            # Truncate description to 100 chars
            opts.append(disnake.SelectOption(label=selectopt, value=str(value), description=description[:100]))
            MySelect.fulldesc.append({"label": selectopt, "value": str(value), "description": description})
            value += 1

        logger.debug(f"opts: {opts}")

        super().__init__(options=opts)

    async def callback(self, inter: disnake.CommandInteraction):
        self.view.stop()
        logger.debug(f"MySelect values: {MySelect.fulldesc}")
        logger.debug(f"values: {self.values[0]}")

        await inter.send(f'You\'ve selected: "{self.options[0]}", send it?')

        msg = await inter.original_message()
        await msg.add_reaction(emoji="👍")

        def check(reaction, user):
            logger.debug("Inside check function")
            return user == inter.author and str(reaction.emoji) == '👍'
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            logger.debug("Timed out")
            await msg.delete()
            await inter.send('You\'re just to damn slow.')
        else:
            await msg.delete()
            logger.debug("We are deleteing stuff now")

            # reasonid = str(removaldict[reason]['id'])
            # subreddit = await redditauth.subreddit("EscapefromTarkov")
            # remreason = await subreddit.mod.removal_reasons.get_reason(reasonid)
            # submission = await redditauth.submission(id=urlffinal, lazy=True)
            # remreasonmsg = str(remreason.message).replace('PLACEHOLDER', urlffinal)
            # await submission.mod.remove(reason_id=remreason.id)
            # await submission.mod.send_removal_message(message=remreasonmsg, title=remreason.title)
            # await ctx.send(f"Sent it, {ctx.author.mention}.  That post is no more.")
            # await msg.delete()


# IN COG:
@bot.slash_command(guild_ids=guilds)
async def select_test(self, inter: disnake.CommandInteraction):
    view = disnake.ui.View()
    view.add_item(MySelect())
    await inter.response.send_message("ORIGINAL", view=view)


bot.run(config['DISCORD']['token'])  # Authenticate to Discord via our local token
