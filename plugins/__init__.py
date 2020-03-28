import inspect
import os

import discord
from collections import namedtuple
import importlib
import logging as log
from traceback import format_exc

Command = namedtuple("Command", "name aliases function description ")
plugins = dict()

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

    plugins[name] = cmd
    return True


def load_plugins():
    for plugin in os.listdir("plugins/"):
        name = os.path.splitext(plugin)[0]
        if not name.startswith("__"):
            load_plugin(name)


def get_plugin(name: str):
    if name in plugins:
        return plugins[name]
    return None


def get_command(trigger: str):
    for plugin in plugins.values():
        commands = getattr(plugin, "__commands", None)
        if not commands:
            continue

        for cmd in plugin.__commands:
            if trigger == cmd.name or trigger in cmd.aliases:
                return cmd
        else:
            continue


def plugin(**options):

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

        log.info("Registered command {} from plugin {}".format(name, plugin.__name__))
        return func

    return decorator
