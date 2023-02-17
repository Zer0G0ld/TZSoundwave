import discord
import asyncio
import youtube_dl
from discord import Intents
from discord.ext import commands

TOKEN = 'seu_token'
PREFIX = '!'
intents = Intents.default()                             intents.members = True                                  client = commands.Bot(command_prefix=PREFIX, intents=intents)

queue = {}

@client.event
async def on_ready():
    print('Bot está On-line!')

@client.command()
async def play(ctx, *, url):
    voice_channel = ctx.author.voice.channel
    if voice_channel is None:
        return await ctx.send('Você precisa estar em um canal de voz para usar este comando!')

    if ctx.voice_client is None:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)

    server = ctx.message.guild
    voice_state = server.voice_client

    ytdl_options = {'format': 'bestaudio'}
    with youtube_dl.YoutubeDL(ytdl_options) as ydl:
        info = ydl.extract_info(url, download=False)
        url = info['formats'][0]['url']
        title = info['title']

    if server.id not in queue:
        queue[server.id] = []

    queue[server.id].append((title, url))

    if voice_state.is_playing():
        return
    else:
        await play_song(server.id, voice_state, ctx)

@client.command()
async def skip(ctx):
    voice_state = ctx.message.guild.voice_client
    if voice_state.is_playing():
        voice_state.stop()

@client.command()
async def stop(ctx):
    voice_state = ctx.message.guild.voice_client
    if voice_state.is_playing():
        voice_state.stop()
    await voice_state.disconnect()

async def play_song(server, voice_state, ctx):
    if len(queue[server]) == 0:
        return

    voice_state.play(discord.FFmpegPCMAudio(queue[server][0][1], **FFMPEG_OPTIONS),
                     after=lambda e: asyncio.run_coroutine_threadsafe(play_song(server, voice_state, ctx), client.loop))
    voice_state.source = discord.PCMVolumeTransformer(voice_state.source)
    voice_state.source.volume = 0.5

    del queue[server][0]
    await ctx.send(f'Playing {voice_state.source.title}')

client.run("TOKEN")
