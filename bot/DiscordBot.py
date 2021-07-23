import configparser
import asyncio
import discord
import random
import datetime
import requests
import re
import os
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from discord import Embed, Member
from bot import shturclass, reddit_login
from typing import Optional

# Loads up the configparser to read our login file
# and build our variables
config = configparser.ConfigParser()
config.read('config')
client = commands.Bot(command_prefix='!')
subredditname = 'EscapefromTarkov'
redditauth = reddit_login.reddit_auth()


@client.event
async def on_ready():
    print("Shturman is running!")
    activity = discord.Activity(name="for commands", type=discord.ActivityType.watching)
    await client.change_presence(activity=activity)


@client.command(aliases=['hi', 'yo', 'hey'])
async def hello(ctx):
    randhello = random.choice(shturclass.Shturclass.hellomsg)
    randmsg = random.choice(shturclass.Shturclass.saymsg)
    await ctx.send(f'{randhello} {ctx.author.mention}! {randmsg}')
    print("Sending hi!")


@client.command(aliases=['goodbye', 'later', 'cya'])
async def bye(ctx):
    randbye = random.choice(shturclass.Shturclass.byemsg)
    await ctx.send(f'{randbye}, {ctx.author.mention}!')


@client.command(aliases=['wq'])
async def watchque(ctx, runprgm, notify="notify", counter=35):
    randhello = random.choice(shturclass.Shturclass.hellomsg)
    runprgm = runprgm.lower()
    guild = client.get_guild(340973813238071298)  # Reddit Mod server guild
    mqchannel = client.get_channel(475755886825177098)  # Reddit Chat Channel
    modmention = guild.get_role(386999610117324800)  # Moderator Role ID
    mqcd = 0
    umcd = 0
    if runprgm == 'disable':
        activity = discord.Activity(name="for commands", type=discord.ActivityType.watching)
        await client.change_presence(activity=activity)
        await ctx.send(f'{randhello} {ctx.author.mention}!, I\'ll no longer monitor the mod queues.')
        quewatcher = False
        return
    if runprgm == 'enable':
        if notify.lower() == "notify":
            await ctx.send(f'{randhello} {ctx.author.mention}!, I\'ll monitor the mod queues, and notify when the queue hits {counter}')
        elif notify.lower() == "false":
            await ctx.send(f'{randhello} {ctx.author.mention}!, I\'ll monitor the mod queues, and won\'t send notifications.')
        else:
            await ctx.send(f'{randhello} {ctx.author.mention}!, I didn\'t understand your syntax.')
            return
        quewatcher = True
        while quewatcher:
            nettest = False  # Checking for network connectivity
            while not nettest:
                try:
                    mqcounter = 0
                    umcounter = 0
                    subreddit = await redditauth.subreddit(subredditname)  # Set our subreddit
                    modmail = await subreddit.modmail.unread_count()
                    async for item in subreddit.mod.modqueue(limit=None):  # Build our Mod Queue #s
                        mqcounter += 1
                    async for item in subreddit.mod.unmoderated(limit=None):  # Build our Unmoderated #s
                        umcounter += 1
                    mmcounter = modmail["new"]
                    discordactivity = f"R:{mqcounter} Q:{umcounter} M:{mmcounter}"  # Update Discord status
                    activity = discord.Activity(name=discordactivity, type=discord.ActivityType.watching)
                    await client.change_presence(activity=activity)
                    if notify.lower() == 'notify':
                        if mqcounter >= counter and mqcd == 0:
                            await mqchannel.send(f"\n{modmention.mention}, the MQ is over 35!")
                            mqcd = 1
                        if umcounter >= counter and umcd == 0:
                            await mqchannel.send(f"\n{modmention.mention}, the UM is over 35!")
                            umcd = 1
                        if (mqcounter <= 3) and (mqcd == 1):
                            print("Resetting MQ cooldown")
                            mqcd = 0
                        if (umcounter <= 3) and (umcd == 1):
                            print("Resetting UM cooldown")
                            umcd = 0
                    await asyncio.sleep(30)
                    nettest = True
                except:
                    print(f'Que watcher || Trying again in 30s')
                    try:
                        print('Loss of connectivity to discord, sleeping for 30s and trying again')
                        activity = discord.Activity(name="connection to Reddit", type=discord.ActivityType.watching)
                        await client.change_presence(activity=activity)
                    except:
                        await asyncio.sleep(30)
                    await asyncio.sleep(30)

        await ctx.send(f'{randhello} {ctx.author.mention}! I\'ll {runprgm} watching the mod queues.')
    else:
        await ctx.send(f'{randhello} {ctx.author.mention}! Sorry, I didn\'t understand your command')


@client.command(aliases=['ms'])
async def media_spam(ctx, runprgm, ignoremod='', action=''):
    from bot import media_spam
    global medialoop
    randhello = random.choice(shturclass.Shturclass.hellomsg)
    runprgm = runprgm.lower()
    ignoremod = ignoremod.lower()
    action = action.lower()
    if runprgm == 'disable':
        await ctx.send(f'{randhello} {ctx.author.mention}!, I\'m turning off media spam checker')
        medialoop.cancel()
        return
    if (runprgm == 'enable') and (ignoremod == 'true' or 'false') and (action == 'remove' or 'report'):
        if runprgm == 'enable':
            await ctx.send(
                f'{randhello} {ctx.author.mention}! I\'ll {runprgm} checking media posts.\n'
                f'Ignore mods: {ignoremod}.\n'
                f'Action: {action}')
            # # media_spam.MediaSpam.run(runprgm, ignoremod, interval, action)
            print("Creating R5 object")
            msstart = media_spam.MediaSpam(runprgm, ignoremod, action)  # Create the mediaspam object to do stuff with
            print("Creating the R5 task")
            medialoop = asyncio.create_task(msstart.run())  # Have to do the create_task, otherwise can't cancel later
            print("Starting the R5 loop!")
            await medialoop
    else:
        await ctx.send(f'{randhello} {ctx.author.mention}! Sorry, I didn\'t understand your command')


@client.command(aliases=['dt'])
async def devtracker(ctx, runprgm):
    randhello = random.choice(shturclass.Shturclass.hellomsg)
    runprgm = runprgm.lower()
    if runprgm == 'disable':
        await ctx.send(f'{randhello} {ctx.author.mention}!, I\'m no longer watching for Dev activity on the subreddit.')
        medialoop.cancel()
        return
    if runprgm == 'enable':
        await ctx.send(f'{randhello} {ctx.author.mention}!, I\'ll start watching for Dev activity on the subreddit.')
        devs = ['trainfender', 'BSG_Cyver']

        async def author_checker(who, link):
            if who in devs:
                print("Found a match: https://www.reddit.com", link)
                devannounce = client.get_channel(668573847062315074)  # official-announcements channel
                await devannounce.send(f"\n {who} posted: https://www.reddit.com{link}")

        async def handle_posts(subreddit):
            async for submission in subreddit.stream.submissions(skip_existing=True):
                await author_checker(submission.author, submission.permalink)

        async def handle_comments(subreddit):
            async for comment in subreddit.stream.comments(skip_existing=True):
                await author_checker(comment.author, comment.permalink)

        async def run():
            subreddit = await redditauth.subreddit("EscapefromTarkov")
            while True:
                try:  # Setting up try for loss of network connectivity
                    things = await asyncio.gather(handle_posts(subreddit), handle_comments(subreddit))
                    return things
                except:
                    print("Lost of network connectivity, trying again in 30s")
                    await asyncio.sleep(30)
        await run()


@client.command(aliases=['shutdown'])
async def turnoff(ctx):
    randhello = random.choice(shturclass.Shturclass.hellomsg)
    await ctx.send(f'{randhello} {ctx.author.mention}, I\'m shutting down :\'(')
    exit()


@client.command(aliases=['information'])
async def info(ctx, target: Optional[Member]):
    target = target or ctx.author
    embed = Embed(title="User information",
                  colour=target.colour,
                  timestamp=datetime.datetime.utcnow())
    fields = [("ID", target.id, False),
              ("Name", str(target), True),
              ("Created at", target.created_at.strftime("%Y-%m-%d %H:%M:%S"), True)]
    #              ("Joined at", target.joined_at.strftime("%Y%m%d %H:%M:%S"), True),
    #              ("Roles", target.roles, True)]
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)
    embed.set_thumbnail(url=target.avatar_url)
    await ctx.send(embed=embed)


@client.command(aliases=['about', 'command'])
async def commands(ctx):
    embed = Embed(title="Commands")
    fields = [('remove_post', "Aliases: `remove`, `r`\n"
                              "Description: This will remove a post when provided a reason and a URL.  Use `!reasons` to see a list of removal reasons"
                              "Shturman will confirm whether or not you want to remove the post.\n"
                              "Switches: Rule# - `1-8`\n"
                              "URL - `Any valid post URL`\n"
                              "Syntax: `!remove Rule# URL`\n "
                              "Example: `!remove 8 https://old.reddit.com/r/EscapefromTarkov/comments/o5u5mn/event_overview_megathread/`",
               False),
              ("media_spam", "Aliases: `ms`.\n"
                             "Description: This will enable or disable checking posts for Rule 5 violations (48hrs)\n"
                             "Switches: runprogram - `enable/disable`\n"
                             "ignoremods - `true/false`\n"
                             "action - `report/remove` \n"
                             "Syntax: `!ms (enbale/disable) (true/false) (report/remove)`\n "
                             "Example: `!ms enable true report`", False),
              ("watchqueue", "Aliases: `wq`.\n"
                             "Description: This will enable or disable watching the moderator queues and sending alerts.\n"
                             "Switches: runprogram - `enable/disable` `notify` `count #`\n"
                             "Syntax: `!wq (enbale/disable)`\n "
                             "Example: `!wq enable false` - Will watch the que but not send messages\n "
                             "`!wq enable notify 50` - Will watch the queue and send notifications at 50.", False),
              ("devtracker", "Aliases: `dt`.\n"
                             "Description: This will enable or disable watching for dev activity on the sub.\n"
                             "Switches: runprogram - `enable/disable`\n"
                             "Syntax: `!dt (enbale/disable)`\n "
                             "Example: `!dt enable`", False),
              ("turnoff", "Aliases: `turnoff`, `shutdown`\n "
                          "Description: This will stop ShturmanBOT from running, only use in case he's being naughty.  Currently broken due to server permissions.\n"
                          "Syntax: `!shutdown`", False),
              ("info", "Description: This will show some information about the user calling the command\n"
                       "Syntax: `!info`", False),
              ("backup_eft", "Aliases: `bu`, `backup`\n"
                             "Description: This will backup the Automoderator, CSS configurations, and CSS images locally.\n"
                             "Switches: Backup Images `true/false`.  Will enable or disable CSS image backup.  Off by default.\n"
                             "Syntax: `!backup true` - Backs up configs & images\n"
                             "Syntax: `!backup` - Backs up configs only.", False)]
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)
    await ctx.send(embed=embed)


@client.command(aliases=[''])
async def analyze(ctx, username):
    randhello = random.choice(shturclass.Shturclass.hellomsg)
    await ctx.send(
        f'{randhello}, {ctx.author.mention}, checking out {username} and their activity on the subreddit, give me a sec...')
    redditor = await reddit_login.reddit_auth().redditor(str(username))
    async for userposts in redditor.submissions.new(limit=20):
        print(userposts)
    async for usercomments in redditor.comments.new(limit=50):
        print(usercomments)


@client.command(aliases=['bu', 'backup'])
async def backup_eft(ctx, images='false'):
    images = images.lower()
    randhello = random.choice(shturclass.Shturclass.hellomsg)
    subredditdata = await reddit_login.reddit_auth().subreddit('EscapefromTarkov')
    await ctx.send(f'Backing up the configurations now....')
    wikipage = await subredditdata.wiki.get_page("config/automoderator")
    nowdate = datetime.datetime.utcnow().strftime("%Y%m%d%M%S")
    filecreate = open(f"F:\\EscapeFromTarkov\\Backups\\Automoderator\\{nowdate}-Automod-Config.txt", "w+")
    filecreate.write(wikipage.content_md)
    filecreate.close()
    substylesheet = await subredditdata.stylesheet()
    filecreate = open(f"F:\\EscapeFromTarkov\\Backups\\CSS\\{nowdate}-CSS-Config.txt", "w+")
    filecreate.write(substylesheet.stylesheet)
    filecreate.close()
    if images == 'true':
        newpath = f'F:\\EscapeFromTarkov\\Backups\\CSS\\{nowdate}-CSS-Images'  # Establish a new directory to house backups
        os.mkdir(newpath)  # Create that directory
        for image in substylesheet.images:  # Loop through every image in the stylesheet
            # Extract the fields we want from the images dictionary
            iurl = image['url']
            iname = image['name']
            ilink = image['link']
            print(f'Name: {iname}, URL: {iurl}, Link: {ilink}')  # Debugging
            dlimage = requests.get(iurl)  # Utilize requests to download the image
            with open(f"F:\\EscapeFromTarkov\\Backups\\CSS\\{nowdate}-CSS-Images\\{iname}.jpg",
                      "wb") as f:  # Open a .jpg image file
                f.write(dlimage.content)  # Write the contents of the image to the file we just opened
    elif images == 'false':
        pass
    await ctx.send(f'{randhello}, {ctx.author.mention}, I\'ve finished backing things up!')


@client.command(aliases=['remove', 'r'])
async def remove_post(ctx, reason, url):
    matcher = re.match('\w*://\w*.reddit.com/r/EscapefromTarkov/comments/', url)
    if not matcher:
        await ctx.send(f'{ctx.author.mention}, you\'ve sent me a fucked up link.')
        return
    try:
        reason = int(reason)
    except:
        await ctx.send(f'{ctx.author.mention}, the reason you provided isn\'t an integer.')
        return

    urlfstep1 = str(url).replace(matcher.group(0), '')
    matcher = re.match('\w*', urlfstep1)
    urlffinal = str(matcher.group(0))

    removaldict = {1: {'id': '1781pn84l7xri', 'name': 'Rule 1:Unrelated Content and Memes'},
                   2: {'id': '1781qciq3mhyw', 'name': 'Rule 2:Content Guidelines'},
                   3: {'id': '1781qjs7b2fmo', 'name': 'Rule 3:Abusive/Poor Behavior'},
                   4: {'id': '1781qngegnpa2', 'name': 'Rule 4:Trading, Begging, and LFG'},
                   5: {'id': '1781qr2mfgaod', 'name': 'Rule 5:Self Advertisement'},
                   6: {'id': '1781qw2kouuv2', 'name': 'Rule 6:Giveaways'},
                   7: {'id': '1781qym93tnhx', 'name': 'Rule 7:Cheating, Exploits, and Piracy'},
                   8: {'id': '1781r1cyetwki', 'name': 'Rule 8:Reposts'}}

    msg = await ctx.message.channel.send(
        f"Are you sure you want to remove {url} for `{removaldict[reason]['name']}`? React with :+1:")

    def check(react, user):
        return react.message.author == msg.author and ctx.message.channel == react.message.channel and react.emoji == '👍'

    try:
        react = await client.wait_for('reaction_add', timeout=20, check=check)
    except asyncio.TimeoutError:
        await msg.delete()
        await ctx.send('You\'re just to damn slow.')
    else:
        await msg.delete()
        msg = await ctx.send(f"Using `{removaldict[reason]['name']}`, to remove this post: {url}")
        reasonid = str(removaldict[reason]['id'])
        subreddit = await redditauth.subreddit("EscapefromTarkov")
        remreason = await subreddit.mod.removal_reasons.get_reason(reasonid)
        submission = await redditauth.submission(id=urlffinal, lazy=True)
        remreasonmsg = str(remreason.message).replace('PLACEHOLDER', urlffinal)
        await submission.mod.remove(reason_id=remreason.id)
        await submission.mod.send_removal_message(message=remreasonmsg, title=remreason.title)
        await ctx.send(f"Sent it, {ctx.author.mention}.  That post is no more.")
        await msg.delete()


@client.command(aliases=['reasons'])
async def removal_reasons(ctx):
    subreddit = await reddit_login.reddit_auth().subreddit('EscapefromTarkov')
    randhello = random.choice(shturclass.Shturclass.hellomsg)
    removestring = ''
    async for item in subreddit.mod.removal_reasons:
        removestring += f'{item.title} \n'
    await ctx.send(f'{randhello}, {ctx.author.mention}, here\'s a list of current removal reasons:\n{removestring}')


@client.command(aliases=['t'])
async def testing(ctx, url):
    pass


@media_spam.error
async def argerror(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention}, your command isn\'t formmated correctly. '
                       f'You need `enable/disable`, `true/false` (for ignoreing mods), '
                       f'`remove/report` (for the action), and a `numeric interval`')
    else:
        raise error


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send(
            f'{ctx.author.mention}, what command are you trying to run? I may not have that implemented yet.')
    else:
        raise error


client.run(config['DISCORD']['token'])  # Run the discord bot
