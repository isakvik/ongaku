import inspect
import os
import discord
from collections import namedtuple
import importlib
import logging as log
from traceback import format_exc

Command = namedtuple("Command", "name aliases function description ")
loaded_plugins = dict()

client = None


def set_client(c: discord.client):
    global client
    client = c


def load_plugin(name: str, package: str = "plugins"):
    try:
        cmd = importlib.import_module("{package}.{plugin}".format(plugin=name, package=package))
    except ImportError as e:
        log.error("couldn't import {package}/{name}\n{e}".format(name=name, package=package, e=format_exc(e)))
        return False

    loaded_plugins[name] = cmd
    return True


def load_plugins():
    for plugin in os.listdir("plugins/"):
        name = os.path.splitext(plugin)[0]
        if not name.startswith("__"):
            load_plugin(name)


async def call_reload(name: str):
    """ Initiates reload of plugin. """
    # See if the plugin has an on_reload() function, and call that
    if hasattr(loaded_plugins[name], "on_reload"):
        if callable(loaded_plugins[name].on_reload):
            result = loaded_plugins[name].on_reload(name)
            if inspect.isawaitable(result):
                await result
    else:
        await on_reload(name)


async def reload_plugins():
    for plugin in loaded_plugins.values():
        name = plugin.__name__.rsplit(".")[-1]
        if not name.startswith("__"):
            await call_reload(name)



def get_plugin(name: str):
    if name in loaded_plugins:
        return loaded_plugins[name]
    return None


def get_command(trigger: str):
    for plugin in loaded_plugins.values():
        commands = getattr(plugin, "__commands", None)
        if not commands:
            continue

        for cmd in plugin.__commands:
            if trigger == cmd.name or trigger in cmd.aliases:
                return cmd
        else:
            continue


def command(**options):

    def decorator(func):
        # create command
        name = options.get("name", func.__name__)
        aliases = options.get("aliases", list())
        description = options.get("description", "No description")

        cmd = Command(name, aliases, func, description)

        # add command to internal list in plugin
        plugin = inspect.getmodule(func)
        commands = getattr(plugin, "__commands", list())
        # TODO: se om attributt er brukt

        commands.append(cmd)

        setattr(plugin, "__commands", commands)

        # TODO: fra pcbot - hva gjør denne?
        # Add the cmd attribute to this function, in order to get the command assigned to the function
        # setattr(func, "cmd", cmd)

        log.info("Created command {} from {}".format(name, plugin.__name__))
        return func

    return decorator


# Default commands

def format_help(cmd: Command, guild: discord.Guild):
    return "help i didnt understand"  # TODO


async def on_reload(name: str):
    if name in loaded_plugins:
        # Remove all registered commands
        if hasattr(loaded_plugins[name], "__commands"):
            delattr(loaded_plugins[name], "__commands")

        loaded_plugins[name] = importlib.reload(loaded_plugins[name])
        log.debug("Reloaded plugin {}".format(name))
