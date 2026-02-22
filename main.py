import os
import threading
import time
from telethon import TelegramClient, events
from unidecode import unidecode
from flask import Flask

# --- CONFIGURATION ---
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

TARGET_ID = int(os.environ.get("TARGET_ID", 0))
TOPIC_ID = os.environ.get("TOPIC_ID")
TOPIC_ID = int(TOPIC_ID) if TOPIC_ID else None

client = TelegramClient("bot", API_ID, API_HASH)

# ===== Flask keep alive =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Alive"

def run_flask():
    port = int(os.environ.get("PORT", 10000))   # 🔥 Render PORT fix
    app.run(host="0.0.0.0", port=port)

# ===== Progress =====
async def progress_callback(current, total, msg, start_time, label):
    now = time.time()
    if (now - start_time) < 2:
        return

    percent = current * 100 / total
    try:
        await msg.edit(f"⚡ {label}: `{percent:.1f}%`")
    except:
        pass

# ===== Handler =====
@client.on(events.NewMessage(incoming=True))
async def handler(event):

    if not event.is_private or not event.media:
        return

    msg = await event.reply("📥 Downloading...")
    start_time = time.time()

    old_caption = event.text or ""
    normal = unidecode(old_caption).upper()

    target_word = "HARSH BHADANA"
    new_text = "🕊️⃝𝚁𝙹's»•βuffal๏•"

    caption = old_caption.replace("HARSH BHADANA", new_text)
    if target_word in normal:
        caption = new_text

    try:
        # Download
        path = await event.download_media(
            progress_callback=lambda c,t: progress_callback(c,t,msg,start_time,"Downloading")
        )

        start_time = time.time()

        # Upload
        await client.send_file(
            TARGET_ID,
            path,
            caption=caption,
            reply_to=TOPIC_ID,
            progress_callback=lambda c,t: progress_callback(c,t,msg,start_time,"Uploading")
        )

        await msg.edit("✅ Done")

        if path and os.path.exists(path):
            os.remove(path)

    except Exception as e:
        await msg.edit(str(e))

# ===== Start =====
async def main():
    await client.start(bot_token=BOT_TOKEN)
    print("🚀 Bot Started")
    await client.run_until_disconnected()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    client.loop.run_until_complete(main())
