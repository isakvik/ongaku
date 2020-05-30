import discord
import plugins
from player import player

voice_clients = {}  # type: dict[discord.Guild, discord.VoiceClient]

if not discord.opus.is_loaded():
    try:
        discord.opus._load_default()
    except OSError:
        pass


@plugins.command(description="Joins the user's voice channel.")
async def connect(message: discord.Message):
    await assert_connected(message)


@plugins.command(description="Plays a specified song.")
async def play(message: discord.Message, *urls):
    await assert_connected(message)
    voice = voice_clients.get(message.guild, None)

    # TODO use player

    # every URL is a song reference
    await message.channel.send(urls)


@plugins.command(description="Plays the PS1 startup sound.")
async def ps1(message: discord.Message):
    await assert_connected(message)
    voice = voice_clients.get(message.guild, None)

    # TODO use player
    source = await discord.FFmpegOpusAudio.from_probe("bin/psone.webm", method='fallback')
    voice.play(source)


async def assert_connected(message: discord.Message):
    chan = seek_voice_chan(message)
    if voice_clients.get(chan.guild, None) and plugins.client in chan.members:
        return voice_clients[chan.guild]

    voice = voice_clients[chan.guild] = await chan.connect()
    assert voice, "could not create voice client..."
    return voice


def seek_voice_chan(message: discord.Message):
    guild = message.guild
    assert isinstance(guild, discord.Guild), "guild not found"

    for chan in guild.voice_channels:
        if message.author in chan.members:
            return chan

    raise AssertionError("you're not in any voice channels")


# @event ## TODO
async def on_disconnect():
    await on_reload("music")


async def on_reload(name: str):
    for voice in voice_clients.values():
        await voice.disconnect()
    voice_clients.clear()

    await plugins.on_reload(name)
