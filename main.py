import os
import discord
import asyncio

from discord import Intents
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord import PCMVolumeTransformer
from discord import Member
from discord import Guild
from dotenv import load_dotenv

import nacl
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
    print(f"Menssagem Recebida: {message.content} ") # Apenas para depuração, fora disso é anti ético

    if not message.author.bot:  # Certifica-se de que o autor da mensagem não seja um bot
        user_id = message.author.id
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

    queue[server.id].append((url, url))  # Simplesmente adicionando a URL duas vezes para simular o título e a URL

    if voice_state.is_playing():
        return
    else:
        await play_song(server.id, voice_state, ctx)

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

async def play_song(server, voice_state, ctx):
    if len(queue[server]) == 0:
        return

    url = queue[server][0][1]

    # Transmitir a música usando FFmpegPCMAudio com a URL fornecida
    voice_state.play(discord.FFmpegPCMAudio(url), after=lambda e: asyncio.run_coroutine_threadsafe(play_song(server, voice_state, ctx), bot.loop))

    # Após tocar a música, remover a música da fila
    del queue[server][0]
    
    # Enviar uma mensagem de reprodução
    await ctx.send(f'Playing {url}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Comando não encontrado.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("Desculpe, você não tem permissão para usar este comando.")
    else:
        await ctx.send("Ocorreu um erro ao executar este comando.")

bot.run(TOKEN)
