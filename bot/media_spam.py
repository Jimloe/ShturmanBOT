import random
import datetime
from bot import reddit_login
from bot import shturclass

# # Authenticate to Reddit
redditauth = reddit_login.reddit_auth()


class MediaSpam(shturclass.Shturclass):
    def __init__(self, runprgm, ignoremod=False, action='report'):
        self.runprgm = runprgm
        self.ignoremod = ignoremod
        self.action = action

    async def run(self):
        removalreason = "Limit posting of linked content to once every 48 hours. Rule 5 applies  " \
                        "to whether or not you made the content you’re submitting. \n\n"
        botspamchannel = 781605968463134790
        subredditstring = f'r/EscapefromTarkov'
        subreddit = 'EscapefromTarkov'
        randhello = random.choice(self.hellomsg)
        urlmatch = ["youtube.com", "twitch.tv", "youtu.be"]
        subredditr5 = await reddit_login.reddit_auth().subreddit(subreddit)
        async for submission in subredditr5.stream.submissions():
            print(f'{submission.title} was submitted')
            for url in urlmatch:  # Loop through youtube & twitch to see if we've got youtube/twitch submissions
                if url in submission.url:  # Finds a match
                    caughtpost = submission.permalink  # Store post in a variable so we can make sure we're not catching it later.
                    print(f'Found a youtube/twitch link: {submission.title}')
                    try: # Setting up try for 404
                        subauthor = submission.author  # Grabs the author.  We want to check their history.
                        # Grabs the time of the post.
                        oppostime = datetime.datetime.fromtimestamp(submission.created_utc)
                        delta = datetime.timedelta(days=2)
                        timecutoff = oppostime - delta
                        # Create a user object and check their post history
                        print(f'Checking the history of {subauthor}')
                        redditor = await reddit_login.reddit_auth().redditor(str(subauthor))
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
                                    if self.action == 'remove':  # Checks to see if we want to remove the post
                                        print('Found one, going to remove the post and leave a message.\n\n\n')
                                        greeting = "{0} {1}! \n\n".format(randhello, submission.author)
                                        footermsg = "***\n\n*I am a bot, and this post was generated automatically. If you believe this was done in error, please contact the " \
                                                    "[mod team](https://www\.reddit\.com/message/compose?to=%2Fr%2FEscapefromTarkov&subject=ShturmanBOT " \
                                                    "error&message=I'm writing to you about the following submission: https://reddit.com{0}. " \
                                                    "%0D%0D ShturmanBOT has removed my post by mistake)*".format(submission.permalink)
                                        commentremovalmsg = greeting + removalreason + footermsg  # Construct removal message
                                        await submission.mod.remove(mod_note="R5 Violation")  # Remove the post
                                        await submission.mod.send_removal_message(commentremovalmsg, type='public')  # Send message
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


    def speak(self):
        print(self.runprgm, self.action, self.interval, self.subreddit)
