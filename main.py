import os
import json
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord.ext import commands

# Lightweight web server for Koyeb port binding
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Multi-bot is online and running!")
        
    def log_message(self, format, *args):
        pass

def run_web_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

async def run_single_bot(token: str, vc_id: int):
    bot = commands.Bot(command_prefix="!", self_bot=True)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user} (ID: {bot.user.id}) for VC: {vc_id}")

    async def maintain_vc():
        await bot.wait_until_ready()
        while not bot.is_closed():
            try:
                channel = bot.get_channel(vc_id)
                if channel and isinstance(channel, discord.VoiceChannel):
                    if not bot.voice_clients or bot.voice_clients[0].channel.id != vc_id:
                        if bot.voice_clients:
                            await bot.voice_clients[0].disconnect(force=True)
                        await channel.connect(self_deaf=True, self_mute=True)
                        print(f"[{bot.user}] Connected to voice channel: {channel.name}")
                else:
                    print(f"[{bot.user}] Voice channel {vc_id} not found.")
            except Exception as e:
                print(f"[{bot.user}] Connection error: {e}")
            await asyncio.sleep(60)

    @bot.event
    async def setup_hook():
        bot.loop.create_task(maintain_vc())

    try:
        await bot.start(token)
    except Exception as e:
        print(f"Bot failed with token ending in ...{token[-6:]}: {e}")

async def main():
    config_raw = os.getenv("BOTS_CONFIG", "[]")
    try:
        bots_data = json.loads(config_raw)
    except Exception as e:
        print(f"Error parsing BOTS_CONFIG JSON: {e}")
        return

    if not bots_data:
        print("Error: BOTS_CONFIG environment variable is empty or invalid.")
        return

    tasks = [run_single_bot(item["token"], int(item["vc_id"])) for item in bots_data]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
