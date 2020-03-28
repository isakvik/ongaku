import asyncio
import traceback
import discord
import logging as log
from argparse import ArgumentParser

import plugins

log.basicConfig(level=log.INFO,
                format="%(asctime)s %(levelname)s:%(name)s :: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S")
discord_log = log.getLogger("discord")
discord_log.setLevel(log.WARN)


class Client(discord.Client):
    def __init__(self):
        super().__init__()

    def dispatch(self, event, *args, **kwargs):
        super().dispatch(event, *args, **kwargs)


client = Client()


@client.event
async def on_ready():
    log.info("Logged in as {0.user} ({0.user.id})".format(client))


@client.event
async def on_message(message: discord.Message):
    # wait until ready
    await client.wait_until_ready()

    # don't care for bots
    if message.author.bot:
        return

    # log own messages..? TODO nødvendig?
    if message.author is client.user:
        log.info("<{0.author.name}> {0.content}".format(message))

    command_prefix = "."  # TODO hardkodet prefix
    if not message.content.startswith(command_prefix):
        return

    cmd_args = message.content[1:].split()

    command = plugins.get_command(cmd_args[0])
    if not command:
        log.info("not a command: {}".format(cmd_args[0]))
        return

    client.loop.create_task(run_command(command, message))


async def run_command(plugin: plugins.Command, message: discord.Message):
    try:
        await plugin.function(message)
    except:
        log.error(traceback.format_exc())


def main():
    parser = ArgumentParser()
    parser.add_argument("--token", "-t", help="Specified login token")
    start_args = parser.parse_args()

    plugins.set_client(client)
    plugins.load_plugins()

    log.info("Starting client...")
    client.run(start_args.token) # TODO move to run config


main()
