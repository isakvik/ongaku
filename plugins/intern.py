import discord
import plugins
import logging


log = logging.getLogger("intern")


@plugins.command(description="Stops the bot.")
async def stop(message: discord.message):
    log.info("Shutting down bot by request.")
    await message.channel.send("cya")
    await plugins.client.logout()


@plugins.command(description="Reloads the plugins for the bot.")
async def reload(message: discord.message):
    log.info("Reloading plugins...")
    await plugins.reload_plugins()
    await message.channel.send("reloaded")


@plugins.command(description="Pings the bot.")
async def ping(message: discord.message):
    log.info("Pinged by user %s.", message.author)
    await message.channel.send("pong")
