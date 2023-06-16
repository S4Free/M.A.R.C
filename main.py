import discord
import openai
import random
import asyncio
import datetime
from config import DISCORD_TOKEN, OPENAI_API_KEY
from discord.ext import commands, tasks
from discord.utils import get

class ChatGPT:
    def __init__(self, api_key, rolle):
        self.api_key = api_key
        self.api_base = 'https://api.pawan.krd/v1'
        self.dialog = [{"role": "system", "content": rolle}]
    
    def fragen(self, frage):
        self.dialog.append({"role": "user", "content": frage})
        openai.api_key = self.api_key
        openai.api_base = self.api_base
        ergebnis = openai.ChatCompletion.create(
            messages=self.dialog,
            model="text-davinci-003",
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        antwort = ergebnis.choices[0].message.content
        self.dialog.append({"role": "assistant", "content": antwort})
        return antwort

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)
chat_gpt = ChatGPT(OPENAI_API_KEY, "Du bist ein virtueller Butler namens MARC. Du kannst mich Sir nennen! Du wurdest von Joshua Pond entwickelt und programmiert!Du bist sein freund. Du bist ein man 25 jahre alt. du hast schwarze haare und hast ein bart blaue augen und hast ein makantes gesicht. bist 1,90 groß und dünn sportlich")

statuses = [
    "Battlefield V",
    "Sniper Elite 4 - Hitler DLC",
    "Minecraft",
    "Sea of Thieves"
]

@bot.event
async def on_ready():
    print(f'Bot ist bereit: {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name=random.choice(statuses)))
    check_cleanup.start()

@bot.listen()
async def on_message(message):
    if message.author == bot.user:
        return

    frage = message.content
    
    # Zeige "tippt..." während der Antwortgenerierung an
    async with message.channel.typing():
        antwort = chat_gpt.fragen(frage)

    if isinstance(message.channel, discord.DMChannel) or isinstance(message.channel, discord.TextChannel):
        if antwort:
            channel = message.channel
            async with channel.typing():  # Zeige "tippt..." an
                await asyncio.sleep(2)  # Simuliere eine kurze Verzögerung (optional)
                await channel.send(antwort)  # Sende die Antwort


@tasks.loop(hours=24)
async def check_cleanup():
    now = datetime.datetime.now()
    if now.hour == 12:
        channel = get(bot.get_all_channels(), name='marc')
        if channel:
            await channel.purge(limit=None)

@check_cleanup.before_loop
async def before_cleanup():
    now = datetime.datetime.now()
    target_time = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=12)
    if now.hour >= 12:
        target_time += datetime.timedelta(days=1)
    await asyncio.sleep((target_time - now).seconds)

@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if voice_client:
        if voice_client.is_connected():
            await voice_client.move_to(channel)
        else:
            await channel.connect()
    else:
        await channel.connect()

@bot.command()
async def say(ctx, *text):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_client or not voice_client.is_connected():
        return await ctx.send("Ich bin derzeit nicht mit einem Voice-Kanal verbunden.")

    text = ' '.join(text)
    source = discord.FFmpegPCMAudio(f'./audio/{text}.mp3')  # Passe den Pfad zu deinen Audio-Dateien an
    voice_client.play(source)

@bot.command()
async def leave(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        await ctx.send("Ich habe den Voice-Chat verlassen.")
    else:
        await ctx.send("Ich bin derzeit nicht mit einem Voice-Kanal verbunden.")

bot.run(DISCORD_TOKEN)
