import asyncpraw
import asyncio
import configparser
import json
from urllib.parse import unquote
import datetime
import random
import requests
import os
import re
import logging

# Loads up the configparser to read our login file
config = configparser.ConfigParser()
config.read('config')

# Logging configuration
logging.basicConfig(format='%(levelname)s-%(asctime)s-%(message)s', level=logging.DEBUG, datefmt='%Y%m%d:%H:%M:%S')


class ShturReddit:

    hellomsg = ['Привет', 'Hello', 'Здорово', 'Hey', 'What\'s up', 'Yo', 'Дороу', 'Здравствуй']
    saymsg = ['How are you today?', 'Pretty shit raids today, eh?', 'Have you seen my Red Rebel anywhere?',
              'Some PMC just stole my key!', 'Jaeger just put a bounty on my head, I\'ll pay you double',
              'Want to go to labs?  I got a keycard.', 'Desync seems bad today, be careful out there.',
              'Have you seen the Svetloozerskiy brothers?  They were supposed to be protecting my loot...',
              'Got any Slickers?', 'Got any Tushonka?', 'Got any Alyonka?', 'Got any TarCola?',
              'Got some mooonshine? Reshala drank all mine ... Vot khuy!', 'Stay off Woods, I\'m hunting PMCs',
              'Have you seen Jaeger\'s camp?', 'Where\'s ZB-014?  Dimon said there was some 60 round mags there.',
              'Armor is for pussies, a jacket is all you need.', 'I heard there was going to be a wipe on Thursday...']

    byemsg = ['Later gator', 'Catch you later', 'Cya', 'Peace out']
    subreddit = "EscapefromTarkov"

    def __init__(self):
        pass

    @staticmethod
    def reddit_auth():
        # Sets up the login for Reddit by reading our config file
        login = asyncpraw.Reddit(username=config['LOGIN']['username'],
                             password=config['LOGIN']['password'],
                             client_id=config['LOGIN']['client_id'],
                             client_secret=config['LOGIN']['client_secret'],
                             user_agent=config['LOGIN']['user_agent'])
        return login

    @staticmethod
    def random_hello():
        return random.choice(ShturReddit.hellomsg)

    @staticmethod
    def random_say():
        return random.choice(ShturReddit.saymsg)

    @staticmethod
    def random_bye():
        return random.choice(ShturReddit.byemsg)

    @staticmethod
    async def queue_counter():
        mqcounter = 0
        umcounter = 0
        reddit = ShturReddit.reddit_auth()
        subreddit = await reddit.subreddit(ShturReddit.subreddit)

        modmail = await subreddit.modmail.unread_count()
        # Build our Mod Queue #s
        async for item in subreddit.mod.modqueue(limit=None):
            mqcounter += 1

        # Build our Unmoderated #s
        async for item in subreddit.mod.unmoderated(limit=None):
            umcounter += 1
        mmcounter = modmail["new"]

        return mqcounter, umcounter, mmcounter

    @staticmethod
    async def backup_eft(images='false'):
        try:
            images = images.lower()
            reddit = ShturReddit.reddit_auth()
            subredditdata = await reddit.subreddit(ShturReddit.subreddit)
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
                    logging.DEBUG(f'Name: {iname}, URL: {iurl}, Link: {ilink}')
                    dlimage = requests.get(iurl)  # Utilize requests to download the image
                    with open(f"F:\\EscapeFromTarkov\\Backups\\CSS\\{nowdate}-CSS-Images\\{iname}.jpg",
                              "wb") as f:  # Open a .jpg image file
                        f.write(dlimage.content)  # Write the contents of the image to the file we just opened
            elif images == 'false':
                pass
            return True
        except Exception as err:
            return err

    @staticmethod
    async def devtracker(chanannounce):
        reddit = ShturReddit.reddit_auth()
        devs = ['trainfender', 'BSG_Cyver']  # Dev Reddit usernames

        async def author_checker(who, link):  # Function for checking posts/comments against our list of devs.
            if who in devs:
                logging.info(f"Found a match: {who} posted: https://www.reddit.com{link}")
                # Announce a find to Discord
                await chanannounce.send(f"\n {who} posted: https://www.reddit.com{link}")

        # We create two streams here, one for posts and one for comments.
        # We combine them later on in the run() function
        async def handle_posts(subreddit):
            async for submission in subreddit.stream.submissions(skip_existing=True):
                await author_checker(submission.author, submission.permalink)

        async def handle_comments(subreddit):
            async for comment in subreddit.stream.comments(skip_existing=True):
                await author_checker(comment.author, comment.permalink)

        async def run():  # Async function that combines both posts and comments.
            subreddit = await reddit.subreddit(ShturReddit.subreddit)
            things = await asyncio.gather(handle_posts(subreddit), handle_comments(subreddit))
            return things

        await run()

    @staticmethod
    async def rule5_enforcer(action):
        removalreason = "Limit posting of linked content to once every 48 hours. Rule 5 applies  " \
                             "to whether or not you made the content you’re submitting. \n\n"
        urlmatch = ["youtube.com", "twitch.tv", "youtu.be"]
        subredditstring = 'r/EscapefromTarkov'
        reddit = ShturReddit.reddit_auth()
        subredditr5 = await reddit.subreddit(ShturReddit.subreddit)
        async for submission in subredditr5.stream.submissions():
            logging.info(f'{submission.title} was submitted')
            for url in urlmatch:  # Loop through youtube & twitch to see if we've got youtube/twitch submissions
                if url in submission.url:  # Finds a match
                    caughtpost = submission.permalink  # Store post in a variable so we can make sure we're not catching it later.
                    logging.info(f'Found a youtube/twitch link: {submission.title}')
                    try:  # Setting up try for 404
                        subauthor = submission.author  # Grabs the author.  We want to check their history.
                        # Grabs the time of the post.
                        oppostime = datetime.datetime.fromtimestamp(submission.created_utc)
                        delta = datetime.timedelta(days=2)
                        timecutoff = oppostime - delta
                        # Create a user object and check their post history
                        logging.info(f'Checking the history of {subauthor}')
                        redditor = await reddit.redditor(str(subauthor))
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
                            logging.info(f'Checking post:"{userhistory.title}"')
                            logging.info(f'Is post time: {historyposttime} between the cutoff: {timecutoff} and now?')
                            if datetime.datetime.fromtimestamp(userhistory.created_utc) < timecutoff:
                                logging.info(f'Outside our time window, stopping.')
                                break
                            # Checks to see if submissions are in our subreddit
                            # If they are, make sure the domain matches twitch or youtube
                            if str(userhistory.subreddit_name_prefixed) == str(subredditstring) and userhistory.domain in urlmatch:
                                logging.info(f'Found a potential match in the {ShturReddit.subreddit}, checking if it is the OP')
                                # We want to make sure we're not matching against the original submission.
                                if userhistory.permalink != caughtpost:
                                    logging.info(f'We found a match: "{userhistory.title}"')
                                    #  Do things like report the post
                                    if action == 'remove':  # Checks to see if we want to remove the post
                                        randhello = ShturReddit.random_hello()
                                        logging.info('Found one, going to remove the post and leave a message.\n\n\n')
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
                                        logging.info(f'Reporting the post: "{submission.title}"\n\n\n')
                                        await submission.report(f'R5 violation check!: {userhistory.id}')
                                        break
                                else:
                                    logging.info(f'"{userhistory.title}" is the OP, skipping it')
                            else:
                                logging.info(f'"{userhistory.title}" is not a media link or within the sub.')
                    except:
                        logging.info("User possibly shadowbanned, do some better error handling")

    @staticmethod
    async def removal_reasons(url, reason, matcher):
        urlfstep1 = str(url).replace(matcher.group(0), '')
        matcher = re.match('\w*', urlfstep1)
        urlffinal = str(matcher.group(0))
        num_rule = reason - 1  # Subtracting 1 due to rule index starting at 0.

        reddit = ShturReddit.reddit_auth()
        subredditdata = await reddit.subreddit(ShturReddit.subreddit)
        wikipage = await subredditdata.wiki.get_page("toolbox")  # Grabbing the wiki page toolbox

        pagedata = wikipage.content_md  # Gets the information off the page
        jdata = json.loads(pagedata)  # This loads the JSON information and enables us to use it
        # This can grab each rule by the specific increment
        # print(jdata['removalReasons']['reasons'][0])
        # 0=R1, 1=R2, 2=R3, 3=R4, 4=R5, 5=R6, 6=R7, 7=R8
        # Parse out our JSON to what we want specifically
        testing = json.dumps(jdata['removalReasons']['reasons'][num_rule]['text'])
        # Remove pesky line feeds.  We have to add these back in later.
        testing = testing.replace('%0A', '#newline')
        outputstr = unquote(testing)  # Converts HTML codes to 'normal' text.
        # Regex matching everything between <option> blocks
        removalreasons = re.findall('(?<=<option>).*?(?=</option>)', outputstr)

        return removalreasons
