import asyncio, logging, os, random, sys

from logging.handlers import RotatingFileHandler

from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait

from pytgcalls import PyTgCalls, filters as fl
from pytgcalls.types import Call, GroupCallConfig, ChatUpdate, Update


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - %(name)s\n%(levelname)s: %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            "logs.txt",
            maxBytes=5000000,
            backupCount=10
        ),
        logging.StreamHandler(),
    ],
)

logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

logs = logging.getLogger()


api_id = 30434687
api_hash = "d4adb52774efd1cbbbebdfc1647b4ee9"
bot_token = "9171816612:AAFTYDEZy0CWPfM1hpZOkAm7J1yc6ouqrh8"
owner_id = 8633636327
controller_group_id = -1003966363333

sessions = [
    "",
    "",

]




# DO NOT MODIFY

bot = Client(
    "userbot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
)

clients = []
call_clients = []
call_config = GroupCallConfig(auto_start=False)

sudo_ids = set()
sudoers = filters.user()
sudoers.add(owner_id)

active_chats = []


async def start_client(name, session):
    try:
        app = Client(
            name=name,
            api_id=api_id,
            api_hash=api_hash,
            session_string=session,
        )

        call = PyTgCalls(app)

        await app.start()
        await call.start()

        clients.append(app)
        call_clients.append(call)

        logs.info(f"✅ Started {name}")

    except Exception as e:
        logs.error(f"Failed to start {name}: {e}")


async def call_services():
    pass
    

async def main():
    for file in os.listdir():
        if file.endswith(".session"):
            os.remove(file)
    for file in os.listdir():
        if file.endswith(".session-journal"):
            os.remove(file)
    try:
        await bot.start()
    except Exception as e:
        logs.error(f"❌ Failed to Start Bot❗\n⚠️ Reason: {e}")
        sys.exit()

    logs.info("✅ Bot Started.")

    tasks = []

    for i, session in enumerate(sessions, start=1):
        tasks.append(
            start_client(f"client_{i}", session)
        )

    await asyncio.gather(*tasks)

    logs.info(f"✅ Started {len(clients)} clients")
    await idle()
    
    
@bot.on_message(filters.command("start") & filters.private)
async def start_handler(_, message):
    await message.reply_text(
        "👋 <b>Welcome!</b>\n\n"
        "🤖 <b>Telegram Userbot Manager</b>\n\n"
        "Use /help to see available commands."
    )


@bot.on_message(filters.command("help") & filters.private)
async def help_handler(_, message):
    text = (
        "🤖 <b>KRISHNA BOT — HELP</b>\n\n"
        "👑 <b>OWNER ONLY</b>\n"
        "• <code>/addsudo USER_ID</code> — Add Sudo\n"
        "• <code>/delsudo USER_ID</code> — Remove Sudo\n\n"
        "🔐 <b>SUDO COMMANDS</b>\n"
        "• <code>/joinvc GROUP_ID</code> — Join voice chat\n"
        "• <code>/leavevc GROUP_ID</code> — Leave voice chat\n"
        "• <code>/joinchat LINK</code> — Join chat\n"
        "• <code>/react MESSAGE_LINK</code> — React to message\n"
        "• <code>/view MESSAGE_LINK</code> — View message\n\n"
        "ℹ️ <b>GENERAL</b>\n"
        "• <code>/start</code> — Start bot\n"
        "• <code>/help</code> — Show commands\n\n"
        "🛡 Owner: Owner only\n"
        "🔑 Sudo: Authorized users only"
    )
    await message.reply_text(text)

@bot.on_message(filters.command("joinchat") & sudoers)
async def join_handler(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Usage:\n/join https://t.me/example"
        )

    chat = message.command[1]
    
    aux = await message.reply_text("🌀 Please Wait...")
    success = []
    async def join(client):
        try:
            await client.join_chat(chat)
            success.append(client)
        except Exception as e:
            pass

    
    results = await asyncio.gather(
        *(join(client) for client in clients),
        return_exceptions=False
    )
    
    total_success = len(success)
    await aux.edit(f"✅ Joined chat {total_success} client's")




joinvc_busy = False

@bot.on_message(filters.command("joinvc") & sudoers & filters.chat(controller_group_id))
async def joinvc_handler(_, message):
    global joinvc_busy
    if joinvc_busy:
        return await message.reply_text("⏳ এত তাড়াতাড়ি কিসের! একটু ওয়েট করো")
    if len(message.command) < 2:
        return await message.reply_text("Usage:\n/joinvc -1001234567890")
    try:
        chat_id = int(message.command[1])
    except Exception:
        return await message.reply_text("Usage:\n/joinvc -1001234567890")

    joinvc_busy = True
    try:
        total = len(call_clients)
        aux = await message.reply_text("🌀 Please Wait...")
        success = 0

        async def join_vc(call):
            nonlocal success
            try:
                await call.play(chat_id)
                await asyncio.sleep(0.5)
                try:
                    await call.mute(chat_id)
                except Exception:
                    pass
                success += 1
            except Exception as e:
                logs.error(f"🚫 Join VC Error: {e}")

        for i in range(0, total, 1):
            await asyncio.gather(
                *(join_vc(call) for call in call_clients[i:i + 1]),
                return_exceptions=True
            )

        await aux.edit(f"✅ Joined {success}/{total} clients.")
    finally:
        joinvc_busy = False
@bot.on_message(filters.command("leavevc") & sudoers & filters.chat(controller_group_id))
async def leavevc_handler(_, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage:\n/leavevc -1001234567890")
    try:
        chat_id = int(message.command[1])
    except Exception:
        return await message.reply_text("Usage:\n/leavevc -1001234567890")

    total = len(call_clients)
    aux = await message.reply_text("🌀 Please Wait...")
    success = 0

    async def leave_vc(call):
        nonlocal success
        try:
            await call.leave_call(chat_id)
            success += 1
        except Exception as e:
            logs.error(f"🚫 Leave VC Error: {e}")

    await asyncio.gather(
        *(leave_vc(call) for call in call_clients),
        return_exceptions=True
    )
    await aux.edit(f"✅ Left {success}/{total} clients.")

@bot.on_message(filters.command("react") & sudoers)
async def react_handler(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Usage:\n/react https://t.me/channel/123"
        )

    link = message.command[1].rstrip("/")

    try:
        parts = link.split("/")

        if "/c/" in link:
            chat_id = int(f"-100{parts[-2]}")
        else:
            chat_id = parts[-2]

        message_id = int(parts[-1])

    except Exception:
        return await message.reply_text("❌ Invalid message link.")

    aux = await message.reply_text("🌀 Please Wait...")

    REACTIONS = ["👍","❤️","🔥","🥰","👏","😁","🎉","🤩","🙏","👌","😍","💯","🏆","❤‍🔥","⚡","😘","😎","🤝","🫡","💘"]
    success = 0

    async def react(client):
        nonlocal success

        try:
            await client.send_reaction(
                chat_id=chat_id,
                message_id=message_id,
                emoji=random.choice(REACTIONS)
            )

            success += 1
            logs.error(f"✅ Reaction sent by {client.name}")

        except Exception as e:
            logs.error(f"❌ Reaction failed [{client.name}]: {e}")
            pass

    await asyncio.gather(*(react(client) for client in clients))
    await aux.edit(f"✅ Reaction sent by {success}/{len(clients)} clients.")
    
    
@bot.on_message(filters.command("view") & sudoers)
async def view_handler(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Usage:\n/view https://t.me/channel/123"
        )

    link = message.command[1].rstrip("/")

    try:
        parts = link.split("/")

        if "/c/" in link:
            chat_id = int(f"-100{parts[-2]}")
        else:
            chat_id = parts[-2]

        message_id = int(parts[-1])

    except Exception:
        return await message.reply_text(
            "❌ Invalid message link."
        )

    aux = await message.reply_text("🌀 Please Wait...")

    success = 0

    async def view(client):
        nonlocal success

        try:
            await client.read_chat_history(
                chat_id,
                message_id
            )

            success += 1
            logs.error(f"✅ Viewed by {client.name}")

        except Exception as e:
            logs.error(f"❌ View failed [{client.name}]: {e}")
            pass

    await asyncio.gather(*(view(client) for client in clients))
    await aux.edit(f"✅ Viewed by {success}/{len(clients)} clients.")
    
    
@bot.on_message(filters.command("addsudo") & filters.user(owner_id))
async def add_sudo(_, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage:\n/addsudo 123456789")
    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid user ID.")
    if user_id == owner_id:
        return await message.reply_text("⚠️ Owner is already authorized.")
    if user_id in sudo_ids:
        return await message.reply_text("⚠️ User is already sudo.")
    sudo_ids.add(user_id)
    sudoers.add(user_id)
    await message.reply_text(f"✅ Added `{user_id}` as sudo.")

@bot.on_message(filters.command("delsudo") & filters.user(owner_id))
async def del_sudo(_, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage:\n/delsudo 123456789")
    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid user ID.")
    if user_id == owner_id:
        return await message.reply_text("❌ Owner ko remove nahi kar sakte.")
    if user_id not in sudo_ids:
        return await message.reply_text("⚠️ User is not sudo.")
    sudo_ids.discard(user_id)
    sudoers.remove(user_id)
    await message.reply_text(f"✅ Removed `{user_id}` from sudo.")

@bot.on_message(filters.command("sudolist") & filters.user(owner_id))
async def sudo_list(_, message):
    ids = sorted(sudo_ids)
    lines = ["👑 <b>KRISHNA BOT — SUDO LIST</b>",
             f"👥 <b>Total Sudo:</b> {len(ids)}"]
    lines.extend(f"• <code>{uid}</code>" for uid in ids)
    await message.reply_text("\n".join(lines))

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
