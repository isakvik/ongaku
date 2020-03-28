import discord
from plugins import plugin


@plugin()
async def play(message: discord.Message):
    try:
        chan = seek_voice_chan(message)
        await chan.connect()

    except Exception as e:
        await message.channel.send(e)


def seek_voice_chan(message: discord.Message):
    guild = message.guild
    if not isinstance(guild, discord.Guild):
        raise Exception("guild not found")

    for chan in guild.voice_channels:
        if message.author in chan.members:
            return chan

    raise Exception("you're not in any voice chans")
