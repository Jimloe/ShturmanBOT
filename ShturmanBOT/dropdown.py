import disnake


# Defines a custom Select containing colour options
# that the user can choose. The callback function
# of this class is called when the user changes their choice
class Dropdown(disnake.ui.Select):
    def __init__(self, optbuilder):
        self.optbuilder = optbuilder
        # Dynamically set our select options from *args
        # *args must be formatted as: 'label="Rule 1", description="Unreleated"'
        options = []
        for arg in self.optbuilder:
            options.append(disnake.SelectOption(arg))
        print(options)

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(
            placeholder="Choose a removal reason...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        await interaction.response.send_message(f"Your selected reason is{self.values[0]}")


class DropdownView(disnake.ui.View):
    def __init__(self, optbuilder):
        super().__init__()
        self.optbuilder = optbuilder

        # Adds the dropdown to our view object.
        self.add_item(Dropdown(optbuilder))


bot = Bot()


@bot.command()
async def colour(ctx):
    """Sends a message with our dropdown containing colours"""

    options = ['"label=1", description="a description"']
    # Create the view containing our dropdown
    view = DropdownView(options)

    # Sending a message containing our view
    await ctx.send("Pick your favourite colour:", view=view)


bot.run("token")
