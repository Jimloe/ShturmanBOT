from bot import DiscordBot
import configparser


# Loads up the configparser to read our login file
config = configparser.ConfigParser()
config.read('config')

# Run our Discord Bot from the python script we've created
DiscordBot.client.run(config['DISCORD']['token'])
