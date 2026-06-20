import asyncio

from telegram import Bot, BotCommand
from telegram.error import Conflict

from tinybot import DEV_GROUP_CHAT_ID, notify_group_chat
from tinybot.tg import BOT_ACCESS_TOKEN

from bot.alerts.handlers import COMMANDS, HANDLERS, cmd_help

POLL_TIMEOUT = 30
READ_TIMEOUT = 40  # must exceed POLL_TIMEOUT or the socket aborts mid-poll
CONFLICT_BACKOFF = 60
ERROR_BACKOFF = 5


async def _dispatch(bot, update) -> None:
    msg = update.message
    if not msg or not msg.text:
        return

    parts = msg.text.split()
    cmd = parts[0].split("@")[0].lower()  # strip @botname
    args = parts[1:]

    handler = HANDLERS.get(cmd, cmd_help)
    try:
        await handler(bot, msg.from_user, msg.chat.id, args)
    except Exception as e:
        print(f"[alerts] handler '{cmd}' error: {e}")


async def telegram_command_loop(bot) -> None:
    """Long-poll Telegram for inbound DMs and dispatch commands. One instance only (one token)."""
    api = Bot(token=BOT_ACCESS_TOKEN)
    await api.initialize()
    await api.delete_webhook(drop_pending_updates=False)  # getUpdates 409s if a webhook is set
    await api.set_my_commands([BotCommand(name, desc) for name, desc in COMMANDS])  # "/" autocomplete menu

    offset = bot.store.get_offset()
    print("[alerts] command loop started")

    while True:
        try:
            updates = await api.get_updates(
                offset=offset,
                timeout=POLL_TIMEOUT,
                read_timeout=READ_TIMEOUT,
                allowed_updates=["message"],
            )
            for update in updates:
                offset = update.update_id + 1
                await _dispatch(bot, update)
            if updates:
                bot.store.set_offset(offset)  # confirm-after-process
        except Conflict as e:
            print(f"[alerts] conflict (another getUpdates running?): {e}")
            await notify_group_chat(f"❌ [alerts] getUpdates conflict: {e}", chat_id=DEV_GROUP_CHAT_ID)
            await asyncio.sleep(CONFLICT_BACKOFF)
        except Exception as e:
            print(f"[alerts] poll error: {e}")
            await asyncio.sleep(ERROR_BACKOFF)
