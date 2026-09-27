import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord.ext import commands

# Lightweight web server to satisfy Render's web service port requirement
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is online and running!")
        
    def log_message(self, format, *args):
        pass # Suppress HTTP access logs to keep console clean

def run_web_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# Start the web server in a separate background thread
threading.Thread(target=run_web_server, daemon=True).start()

# Initialize discord self-bot
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
        
        await asyncio.sleep(60)

if __name__ == "__main__":
    if not TOKEN or not VC_ID:
        print("Error: DISCORD_TOKEN and VC_ID environment variables must be set.")
    else:
        bot.run(TOKEN, reconnect=True)
