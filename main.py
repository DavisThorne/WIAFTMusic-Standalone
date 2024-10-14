import os
import discord
from discord.ext import commands
import lavaplay
import dotenv

class EnvDoesNotExist(Exception):
    def __init__(self, message="The .env file does not exist, creating a default file"):
        self.message = message
        dotenv.set_key(".env", "TOKEN",
                       "bots_token_here",
                       quote_mode="never")
        dotenv.set_key(".env", "GUILD_ID",
                          "guild_id_here",
                          quote_mode="never")
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"


client = commands.Bot(intents=discord.Intents.all(), command_prefix='!')

lavalink = lavaplay.Lavalink()
node_main = lavalink.create_node(
    user_id=1,
    host="localhost",
    port=2333,
    password="youshallnotpass"
)

if not os.path.exists(".env"):
    raise EnvDoesNotExist

dotenv.load_dotenv(".env")

TOKEN = str(os.getenv("TOKEN"))

try:
    node_main.connect()
except Exception:
    print("Failed to connect to Lavalink node")

@client.event
async def on_ready():
    print(f"Logged in as {client.user.name}")
    node_main.connect()

@client.slash_command(name="ping", description="Checks bots latency")
async def ping(ctx):
    await ctx.respond(f'Pong! {round(client.latency * 1000)}ms')

@client.slash_command(name="setup", description="Sets up the bot for the server")
async def setup(ctx):
    guild_id = ctx.guild.id
    dotenv.set_key(".env", "GUILD_ID", str(guild_id), quote_mode="never")
    await ctx.respond(f"Guild ID set to {guild_id}")




client.run(TOKEN)