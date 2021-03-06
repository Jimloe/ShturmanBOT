import disnake
import asyncio
import logging
from reddit_helper import ShturReddit

# Logging configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(name)s-%(message)s', datefmt='%Y%m%d:%H:%M:%S')
file_handler = logging.FileHandler('logfile.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


class SelectUI(disnake.ui.Select):

    fulldesc = []
    url = ""
    matcher = ""

    def __init__(self, removals, bot):
        self.removals = removals
        self.bot = bot

        opts = []
        value = 1
        for i in self.removals:
            selectopt = str(i['label'])
            description = str(i['description'])
            # Truncate description to 100 chars
            opts.append(disnake.SelectOption(label=selectopt, value=str(value), description=description[:100]))
            SelectUI.fulldesc.append({"label": selectopt, "value": str(value), "description": description})
            value += 1

        logger.debug(f"opts: {opts}")

        super().__init__(options=opts)

    async def callback(self, inter: disnake.CommandInteraction):
        self.view.stop()  # Break original select menu because I don't know how to delete the message >.>

        logger.debug(f"MySelect values: {SelectUI.fulldesc}")
        logger.debug(f"values: {self.values}")
        reasonnum = int(self.values[0]) - 1  # Subtracting one to line up the Discord selection w/ the python list.

        await inter.send(f'You\'ve selected: "{self.options[reasonnum]}", send it?')

        msg = await inter.original_message()
        await msg.add_reaction(emoji="👍")

        def check(reaction, user):
            logger.debug("Inside check function")
            return user == inter.author and str(reaction.emoji) == '👍'
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            logger.debug("Timed out")
            await msg.delete()
            await inter.send('Timed out, please try again.')
        else:
            await msg.delete()
            logger.debug(
                f"Delete post, specific Removal reasons: R{SelectUI.fulldesc[reasonnum]['label']}: "
                f"{SelectUI.fulldesc[reasonnum]['description']}"
            )

            removenotice = await ShturReddit.remove_post(
                url=SelectUI.url,
                matcher=SelectUI.matcher,
                rrnum=SelectUI.fulldesc[reasonnum]['label'],
                rrmsg=SelectUI.fulldesc[reasonnum]['description']
            )
            if removenotice:
                await inter.send(
                    f"{inter.author.name} has removed {SelectUI.url} for "
                    f"{SelectUI.fulldesc[reasonnum]['label']}:"
                    f"{SelectUI.fulldesc[reasonnum]['description']}"
                )
