import asyncio
import inspect
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

    ### this handles events in the client
    # def dispatch(self, event, *args, **kwargs):
    #    super().dispatch(event, *args, **kwargs)


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

    command_prefix = "."  # TODO hardkodet prefix
    content = message.content[len(command_prefix):]

    # make sure this is a command
    if not message.content.startswith(command_prefix) or not content or content.startswith(" "):
        return

    content_words = content.split()
    cmd_name, given_args = content_words[0], content_words[1:]

    command = plugins.get_command(cmd_name)
    if not command:
        log.info("not a command: {}".format(cmd_name))
        return

    cmd_args, complete = parse_given_args(command, message, given_args)
    if not complete:
        log.info("missing arguments: {}".format(cmd_args))
        return

    client.loop.create_task(run_command(command, message, *cmd_args))


@client.event
async def on_disconnect():
    # TODO: register event handlers in plugins instead
    # plugins.recover_from_disconnection()
    print("disconnected")


def parse_given_args(command: plugins.Command, message: discord.Message, given_args):
    # Parse given arguments for command into list of arguments to use in function call
    signature = inspect.signature(command.function)
    args = []
    complete = False
    req_args = len(signature.parameters.values())

    index = 0
    for param in signature.parameters.values():
        # Skip first argument as it's always a discord.Message
        index += 1

        if index <= len(given_args):
            cmd_arg = given_args[index - 1]
            args.append(cmd_arg)
        else:
            if param.default is not param.empty:
                args.append(param.default)
                continue
            else:
                break

        if param.kind is not param.VAR_POSITIONAL:
            req_args -= 1

        # TODO: transformation annotations - parse_annotation(anno, message, cmd_arg)

    if req_args <= len(args) + 1:
        complete = True

    # print(given_args)
    # print(args)
    # print(complete)
    return args, complete


async def run_command(command: plugins.Command, message: discord.Message, *cmd_args):
    try:
        await command.function(message, *cmd_args)
    except AssertionError as e:
        # user error
        await message.channel.send(str(e) or plugins.format_help(command, message.guild))
    except:
        # uncaught error
        log.error(traceback.format_exc())
        await message.channel.send("whoops, an unknown error occurred")


def main():
    parser = ArgumentParser()
    parser.add_argument("--token", "-t", help="Specified login token", required=True)
    start_args = parser.parse_args()

    plugins.set_client(client)
    plugins.load_plugins()

    log.info("Starting client...")
    client.run(start_args.token)


main()
