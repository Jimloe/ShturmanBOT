import asyncpraw
import configparser

# Loads up the configparser to read our login file
config = configparser.ConfigParser()
config.read('config')


def reddit_auth():
    # Sets up the login for Reddit
    r = asyncpraw.Reddit(username=config['LOGIN']['username'],
                                   password=config['LOGIN']['password'],
                                   client_id=config['LOGIN']['client_id'],
                                   client_secret=config['LOGIN']['client_secret'],
                                   user_agent=config['LOGIN']['user_agent'])
    return r
