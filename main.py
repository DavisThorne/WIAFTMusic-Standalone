import re
import os
import discord
from discord.ext import commands
import lavalink
import dotenv
import asyncio

class EnvDoesNotExist(Exception):
    def __init__(self, message="The .env file does not exist, creating a default file"):
        self.message = message
        dotenv.set_key(".env", "TOKEN",
                       "bots_token_here",
                       quote_mode="never")
        dotenv.set_key(".env", "GUILD_ID",
                        "guild_id_here",
                        quote_mode="never")
        dotenv.set_key(".env", "USER_ID",
                        "bots_user_id_here",
                        quote_mode="never")

        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"

client = commands.Bot(intents=discord.Intents.all(), command_prefix='!')
url_rx = re.compile(r'https?://(?:www\.)?.+')

if not os.path.exists(".env"):
    raise EnvDoesNotExist

dotenv.load_dotenv(".env")

TOKEN = str(os.getenv("TOKEN"))
GUILD_ID = str(os.getenv("GUILD_ID"))
USER_ID = str(os.getenv("USER_ID"))

class LavaPlayerBot(discord.VoiceProtocol, commands.Cog, name="LavaPlayer"):
    async def initialize_lavalink(self):
        self.client.lavalink = lavalink.Client(self.user_id)
        self.lavalink = self.client.lavalink
        self.lavalink.add_node(
            host="localhost",
            port="2333",
            password="youshallnotpass",
            region="GB",
            name="main-node"
        )
        print("Connected")

    def __init__(self, client, user_id, guild_id, channel=discord.abc.Connectable):
        self.client = client
        self.channel = channel
        self.guild_id = guild_id
        self.user_id = user_id
        #asyncio.run(self.initialize_lavalink())

    @commands.slash_command(name="ping", description="Checks bots latency")
    async def ping(self, ctx):
        await ctx.respond(f'Pong! {round(client.latency * 1000)}ms')

    @commands.slash_command(name="setup", description="Sets up the bot for the server")
    async def setup(self, ctx):
        self.guild_id = ctx.guild.id
        self.user_id = client.user.id
        dotenv.set_key(".env", "GUILD_ID", str(self.guild_id), quote_mode="never")
        dotenv.set_key(".env", "USER_ID", str(self.user_id), quote_mode="never")
        await ctx.respond(f"Guild ID set to {guild_id}")

    @commands.slash_command(name="play", description="plays a song with the music bot")
    async def play(self, ctx):
        ctx.respond("temp")

@client.event
async def on_ready():
    print(f"Logged in as {client.user.name}")
    print(f"{client.user.id}")
    lpb = LavaPlayerBot(client, USER_ID, GUILD_ID)
    await lpb.initialize_lavalink()


#LavaPlayerBot.initialize_lavalink(self=LavaPlayerBot)
client.add_cog(LavaPlayerBot(client, USER_ID, GUILD_ID))
client.run(TOKEN)
