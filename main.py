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
    def __init__(self, user_id, guild_id, client, channel=discord.abc.Connectable):
        self.client = client
        self.channel = channel
        self.guild_id = guild_id
        self.user_id = user_id
        self.player = None

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
        print(f"{self.lavalink}")
        await self.createLavalinkPlayer()
        return self.lavalink
    
    async def createLavalinkPlayer(self, ctx):
        self.lavalink.player_manager.create(self.guild_id)
        self.player = ctx.bot.lavalink.player_manager.create(self.guild_id)

    @commands.slash_command(name="ping", description="Checks bots latency")
    async def ping(self, ctx):
        await ctx.respond(f'Pong! {round(self.client.latency * 1000)}ms')

    @commands.slash_command(name="setup", description="Sets up the bot for the server")
    async def setup(self, ctx):
        self.guild_id = ctx.guild.id
        self.user_id = self.client.user.id
        dotenv.set_key(".env", "GUILD_ID", str(self.guild_id), quote_mode="never")
        dotenv.set_key(".env", "USER_ID", str(self.user_id), quote_mode="never")
        await self.initialize_lavalink()
        await ctx.respond(f"Guild ID set to {self.guild_id}")

    @commands.slash_command(name="join", description="Bot will join what voice channel you are in", guild_ids=[GUILD_ID])
    async def join(self, ctx):
        if self.player == None:
            await self.createLavalinkPlayer(ctx)
        if ctx.author.voice is None:
            return await ctx.respond("You currently arent in a voice channel")
        voice_client = ctx.voice_client
        voice_channel = ctx.author.voice.channel
        await voice_channel.connect()
        

    @commands.slash_command(name="play", description="plays a song with the music bot")
    async def play(self, ctx):
        await ctx.respond("temp")

    @commands.Cog.listener()
    async def on_ready(self):
        print(self.client)
        print(f"Logged in as {str(self.client.user.name)}")
        print(f"{str(self.client.user.id)}")
        await self.initialize_lavalink( )

lpb = LavaPlayerBot(USER_ID, GUILD_ID, client)
lpb.client.add_cog(LavaPlayerBot(USER_ID, GUILD_ID, client))
lpb.client.run(TOKEN)

