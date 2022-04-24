import discord
from discord.ext import commands

token = open("token.txt", "r").readline()

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = '.', intents=intents)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="your calendar!"))
    print(f'{client.user} has connected to Discord!')

