import discord


class Client(discord.Client):
    def __init__(self):
        print("Hello, World!")


client = Client()
