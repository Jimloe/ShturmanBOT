from bot import reddit_login
from bot import shturclass

# # Authenticate to Reddit
redditauth = reddit_login.reddit_auth()


class SubStream(shturclass.Shturclass):
    def __init__(self, runprgm):
        self.runprgm = runprgm

    async def run(self):
        self.subreddit
        modannouncechannel = 397726179257352196
        subredditr5 = await reddit_login.reddit_auth().subreddit(self.subreddit)
        async for submission in subredditr5.stream.submissions():
            pass