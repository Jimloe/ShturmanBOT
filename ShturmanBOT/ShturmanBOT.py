import asyncio
import configparser
import requests
import os
import datetime
import random
import shturclass
from ShturmanBOT.ShturmanBOT import reddit_helper
import disnake
from disnake.ext import commands

# Invite URL: https://discord.com/api/oauth2/authorize?client_id=721249120190332999&permissions=328565075008&scope=bot%20applications.commands

# Loads up the configparser to read our login file
config = configparser.ConfigParser()
config.read('config')

# Creating a commands.Bot() instance and using 'bot'
bot = commands.Bot()

reddit = reddit_login.reddit_auth()  # Authenticate to Reddit using Shturman creds.
eftsub = shturclass.Shturclass.subreddit

# Setup allowed mentions by Discord bot
disnake.AllowedMentions(everyone=True, users=True, roles=True, replied_user=True)

guilds = config['DISCORD']['guilds']


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


@bot.slash_command(guild_ids=guilds)
async def watch_queue(inter, runprgm, notify):
    counter = 35
    modguild = bot.get_guild(int(config['DISCORD']['eftserver']))  # EFT Discord server
    # chan_alerts = bot.get_channel(int(config['DISCORD']['eftannounce'])  # EFT Announcements
    chan_alerts = bot.get_channel(int(config['DISCORD']['probochan']))  # EFT Probo chat channel
    modmention = modguild.get_role(int(config['DISCORD']['modrole']))  # EFT Moderator Role
    modmentionprob = modguild.get_role(int(config['DISCORD']['proborole']))  # EFT Probo Role
    randhello = random.choice(shturclass.Shturclass.hellomsg)
    runprgm = runprgm.lower()
    mqchannel = chan_alerts
    mqcd = 0  # Mod Queue counter
    umcd = 0  # Unmod Queue counter
    if runprgm == 'disable':  # Change the activity to reflect that we aren't watching the queue any longer.
        activity = disnake.Activity(name="for commands", type=disnake.ActivityType.watching)
        await bot.change_presence(activity=activity)
        await inter.send(f'{randhello} {inter.author.mention}!, I\'ll no longer monitor the mod queues.')
        quewatcher = False
        return
    if runprgm == 'enable':
        if notify.lower() == "true":
            await inter.send(
                f'{randhello} {inter.author.mention}!, I\'ll monitor the mod queues, and notify when the queue hits {counter}')
        elif notify.lower() == "false":
            await inter.send(
                f'{randhello} {inter.author.mention}!, I\'ll monitor the mod queues, and won\'t send notifications.')
        else:
            await inter.send(f'{randhello} {inter.author.mention}!, I didn\'t understand your syntax.')
            return
        quewatcher = True
        while quewatcher:
            nettest = False  # Checking for network connectivity
            while not nettest:
                try:
                    mqcounter = 0
                    umcounter = 0
                    subreddit = await reddit.subreddit(eftsub)  # Set our subreddit
                    modmail = await subreddit.modmail.unread_count()
                    async for item in subreddit.mod.modqueue(limit=None):  # Build our Mod Queue #s
                        mqcounter += 1
                    async for item in subreddit.mod.unmoderated(limit=None):  # Build our Unmoderated #s
                        umcounter += 1
                    mmcounter = modmail["new"]
                    discordactivity = f"R:{mqcounter} Q:{umcounter} M:{mmcounter}"  # Update Discord status
                    activity = disnake.Activity(name=discordactivity, type=disnake.ActivityType.watching)
                    await bot.change_presence(activity=activity)
                    if notify.lower() == 'notify':
                        if mqcounter >= counter and mqcd == 0:
                            await mqchannel.send(f"\n{modmention.mention}, {modmentionprob.mention}, the MQ is over 35!")
                            mqcd = 1
                        if umcounter >= counter and umcd == 0:
                            await mqchannel.send(f"\n{modmention.mention}, {modmentionprob.mention} the UM is over 35!")
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
                        activity = disnake.Activity(name="connection to Reddit", type=disnake.ActivityType.watching)
                        await bot.change_presence(activity=activity)
                    except:
                        await asyncio.sleep(30)
                    await asyncio.sleep(30)

        await inter.send(f'{randhello} {inter.author.mention}! I\'ll {runprgm} watching the mod queues.')
    else:
        await inter.send(f'{randhello} {inter.author.mention}! Sorry, I didn\'t understand your command')


@bot.slash_command(guild_ids=guilds)
async def devtracker(ctx, runprgm):
    chan_announce = bot.get_channel(668573847062315074)  # EFT Announcements channel
    randhello = random.choice(shturclass.Shturclass.hellomsg)
    devannounce = chan_announce  # Jimlos Test announcements channel
    runprgm = runprgm.lower()
    if runprgm == 'disable':
        await ctx.send(f'{randhello} {ctx.author.mention}!, Jimlo doesn\'t know how to code this yet ... fucking scrub.')
        # lol fucking handle it, this is broken in old version.
        return
    if runprgm == 'enable':
        await ctx.send(f'{randhello} {ctx.author.mention}!, I\'ll start watching for Dev activity on the subreddit.')
        devs = ['trainfender', 'BSG_Cyver']  # Reddit usernames of devs

        async def author_checker(who, link):  # Function for checking posts/comments against our list of devs.
            if who in devs:
                print("Found a match: https://www.reddit.com", link)
                await devannounce.send(f"\n {who} posted: https://www.reddit.com{link}")

        # We create two streams here, one for posts and one for comments.
        # We combine them later on in the run() function
        async def handle_posts(subreddit):
            async for submission in subreddit.stream.submissions(skip_existing=True):
                await author_checker(submission.author, submission.permalink)

        async def handle_comments(subreddit):
            async for comment in subreddit.stream.comments(skip_existing=True):
                await author_checker(comment.author, comment.permalink)

        async def run():  # Async function that combines both posts and comments.
            subreddit = await reddit.subreddit(eftsub)
            while True:
                try:  # Setting up try for loss of network connectivity
                    things = await asyncio.gather(handle_posts(subreddit), handle_comments(subreddit))
                    return things
                except:
                    print("Lost of network connectivity, trying again in 30s")
                    await asyncio.sleep(30)
        await run()


@bot.slash_command(guild_ids=guilds, aliases=['bu', 'backup'])
async def backup_eft(ctx, images='false'):
    images = images.lower()
    randhello = random.choice(shturclass.Shturclass.hellomsg)
    subredditdata = await reddit.subreddit('EscapefromTarkov')
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


# Module in progress
@bot.slash_command(guild_ids=guilds)
async def rule5_enforcer(inter, action):
    randhello = random.choice(shturclass.Shturclass.hellomsg)
    await inter.response.send_message(f"{randhello} {inter.author.mention}!  I'll start enforcing Rule 5 on the sub.")
    removalreason = "Limit posting of linked content to once every 48 hours. Rule 5 applies  " \
                    "to whether or not you made the content you’re submitting. \n\n"
    subredditstring = f'r/EscapefromTarkov'
    subreddit = 'EscapefromTarkov'
    urlmatch = ["youtube.com", "twitch.tv", "youtu.be"]
    subredditr5 = await reddit_helper.reddit_auth().subreddit(subreddit)
    async for submission in subredditr5.stream.submissions():
        print(f'{submission.title} was submitted')
        for url in urlmatch:  # Loop through youtube & twitch to see if we've got youtube/twitch submissions
            if url in submission.url:  # Finds a match
                caughtpost = submission.permalink  # Store post in a variable so we can make sure we're not catching it later.
                print(f'Found a youtube/twitch link: {submission.title}')
                try:  # Setting up try for 404
                    subauthor = submission.author  # Grabs the author.  We want to check their history.
                    # Grabs the time of the post.
                    oppostime = datetime.datetime.fromtimestamp(submission.created_utc)
                    delta = datetime.timedelta(days=2)
                    timecutoff = oppostime - delta
                    # Create a user object and check their post history
                    print(f'Checking the history of {subauthor}')
                    redditor = await reddit_helper.reddit_auth().redditor(str(subauthor))
                    async for userhistory in redditor.submissions.new(limit=10):
                        # for userhistory in reddit_login.redditor(str(subauthor)).submissions.new(limit=10): Old - Remove
                        # Checks to see if a submission has been removed, if so we want to ignore it
                        try:
                            if userhistory.removed is True:
                                continue  # The post has been removed, continue on to next submission
                        except:
                            pass  # The post has not been removed, so we want to move on to the rest of the script
                        # Checks post time to make sure we're not going too far back and doing excess checking.
                        historyposttime = datetime.datetime.fromtimestamp(userhistory.created_utc)
                        print(f'Checking post:"{userhistory.title}"')
                        print(f'Is post time: {historyposttime} between the cutoff: {timecutoff} and now?')
                        if datetime.datetime.fromtimestamp(userhistory.created_utc) < timecutoff:
                            print(f'Outside our time window, stopping.')
                            break
                        # Checks to see if submissions are in our subreddit
                        # If they are, make sure the domain matches twitch or youtube
                        if str(userhistory.subreddit_name_prefixed) == str(subredditstring) and userhistory.domain in urlmatch:
                            print(f'Found a potential match in the {subreddit}, checking if it is the OP')
                            # We want to make sure we're not matching against the original submission.
                            if userhistory.permalink != caughtpost:
                                print(f'We found a match: "{userhistory.title}"')
                                #  Do things like report the post
                                if action == 'remove':  # Checks to see if we want to remove the post
                                    randhello = random.choice(shturclass.Shturclass.hellomsg)
                                    print('Found one, going to remove the post and leave a message.\n\n\n')
                                    greeting = "{0} {1}! \n\n".format(randhello, submission.author)
                                    footermsg = "***\n\n*I am a bot, and this post was generated automatically. If you believe this was done in error, please contact the " \
                                                "[mod team](https://www\.reddit\.com/message/compose?to=%2Fr%2FEscapefromTarkov&subject=ShturmanBOT " \
                                                "error&message=I'm writing to you about the following submission: https://reddit.com{0}. " \
                                                "%0D%0D ShturmanBOT has removed my post by mistake)*".format(submission.permalink)
                                    commentremovalmsg = greeting + removalreason + footermsg  # Construct removal message
                                    await submission.mod.remove(mod_note="R5 Violation")  # Remove the post
                                    await submission.mod.send_removal_message(commentremovalmsg,
                                                                              type='public')  # Send message
                                else:  # If we don't have post removal set, then we want to report the post.
                                    print(f'Reporting the post: "{submission.title}"\n\n\n')
                                    await submission.report(f'R5 violation check!: {userhistory.id}')
                                    break
                            else:
                                print(f'"{userhistory.title}" is the OP, skipping it')
                        else:
                            print(f'"{userhistory.title}" is not a media link or within the sub.')
                except:
                    print("User possibly shadowbanned, do some better error handling")


@bot.slash_command(guild_ids=guilds, aliases=['help'])
async def help_shturman(inter):
    embed = embeder("This lists out important commands!")
    embed.add_field(name="Regular Title", value="Regular Value", inline=False)
    embed.add_field(name="Inline Title", value="Inline Value", inline=True)
    embed.add_field(name="Inline Title", value="Inline Value", inline=True)
    embed.add_field(name="Inline Title", value="Inline Value", inline=True)

    await inter.response.send_message(embed=embed)


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

bot.run(config['DISCORD']['token'])  # Authenticate to Discord via our local token
