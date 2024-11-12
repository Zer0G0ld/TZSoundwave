import os
import discord
import asyncio
from discord import Intents
from discord.ext import commands
from discord import FFmpegPCMAudio
from dotenv import load_dotenv
import youtube_dl

load_dotenv()

TOKEN = os.getenv('TOKEN')
PREFIX = '!'
intents = Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

queue = {}

@bot.event
async def on_ready():
    print(f"=================================")
    print(f"Estou Online como {bot.user.name}")
    print(f"=================================")

@bot.event
async def on_message(message):
    print(f"Mensagem Recebida: {message.content}")  # Apenas para depuração, fora disso é antiético

    if not message.author.bot:  # Certifica-se de que o autor da mensagem não seja um bot
        await bot.process_commands(message)

@bot.command()
async def oi(ctx):
    await ctx.send(f"Olá!")

@bot.command()
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

    if server.id not in queue:
        queue[server.id] = []

    song = await download_song(url)
    queue[server.id].append(song)

    if not voice_state.is_playing():
        await play_song(server.id, voice_state, ctx)

async def download_song(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        return url2

async def play_song(server, voice_state, ctx):
    if len(queue[server]) == 0:
        return

    song_url = queue[server][0]

    # Transmitir a música usando o URL obtido do YouTube
    voice_state.play(FFmpegPCMAudio(song_url), after=lambda e: asyncio.run_coroutine_threadsafe(play_song(server, voice_state, ctx), bot.loop))

    # Após tocar a música, remover a música da fila
    del queue[server][0]
    
    # Enviar uma mensagem de reprodução
    await ctx.send(f'Estou tocando: {song_url}')

@bot.command()
async def skip(ctx):
    voice_state = ctx.message.guild.voice_client
    if voice_state.is_playing():
        voice_state.stop()

@bot.command()
async def stop(ctx):
    voice_state = ctx.message.guild.voice_client
    if voice_state.is_playing():
        voice_state.stop()
    await voice_state.disconnect()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Comando não encontrado.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("Desculpe, você não tem permissão para usar este comando.")
    else:
        await ctx.send("Ocorreu um erro ao executar este comando.")

bot.run(TOKEN)
