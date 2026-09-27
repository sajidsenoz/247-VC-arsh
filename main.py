import os
import asyncio
import discord
from discord.ext import commands

# Initialize client using discord.py-self for user token support
bot = commands.Bot(command_prefix="!", self_bot=True)

VC_ID = int(os.getenv("VC_ID", "0"))
TOKEN = os.getenv("DISCORD_TOKEN", "")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await join_vc()

async def join_vc():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            channel = bot.get_channel(VC_ID)
            if channel and isinstance(channel, discord.VoiceChannel):
                if not bot.voice_clients or bot.voice_clients[0].channel.id != VC_ID:
                    if bot.voice_clients:
                        await bot.voice_clients[0].disconnect(force=True)
                    await channel.connect(self_deaf=True, self_mute=True)
                    print(f"Connected to voice channel: {channel.name}")
            else:
                print(f"Voice channel with ID {VC_ID} not found.")
        except Exception as e:
            print(f"Connection error: {e}")
        
        # Check connection status every 60 seconds
        await asyncio.sleep(60)

if __name__ == "__main__":
    if not TOKEN or not VC_ID:
        print("Error: DISCORD_TOKEN and VC_ID environment variables must be set.")
    else:
        bot.run(TOKEN, reconnect=True)