from tinybot import DEV_GROUP_CHAT_ID, notify_group_chat

from bot.config import MAX_ADDRESSES_PER_USER, labeled_address, parse_address

HELP = (
    "📡 <b>Flex Alerts</b>\n\n"
    "Add an address to your watchlist and get a DM whenever one of its Troves is opened, "
    "adjusted, liquidated or redeemed.\n\n"
    "<b>Commands</b>\n"
    "/add [address] - add an address to your watchlist\n"
    "/remove [address] - remove an address from your watchlist\n"
    "/list - show your watchlist\n"
    "/help - show this message\n\n"
    f"Your watchlist can hold up to {MAX_ADDRESSES_PER_USER} addresses. Contact devs if you need more."
)


def _who(user) -> str:
    """A human-friendly identifier for a Telegram user."""
    if user.username:
        return f"@{user.username}"
    return user.full_name or str(user.id)


async def cmd_start(bot, user, chat_id: int, args: list[str]) -> None:
    bot.store.ensure_user(user.id, chat_id)
    await notify_group_chat(HELP, chat_id=chat_id)


async def cmd_help(bot, user, chat_id: int, args: list[str]) -> None:
    await notify_group_chat(HELP, chat_id=chat_id)


async def cmd_add(bot, user, chat_id: int, args: list[str]) -> None:
    if not args:
        await notify_group_chat("Usage: /add [address]", chat_id=chat_id)
        return

    address = parse_address(args[0])
    if address is None:
        await notify_group_chat("That's not a valid address.", chat_id=chat_id)
        return

    result = bot.store.add_address(user.id, chat_id, address, MAX_ADDRESSES_PER_USER)
    if result == "exists":
        await notify_group_chat("Already on your watchlist.", chat_id=chat_id)
    elif result == "cap":
        await notify_group_chat(
            f"Your watchlist is full ({MAX_ADDRESSES_PER_USER} addresses max). Contact devs if you need more.",
            chat_id=chat_id,
        )
    else:
        await notify_group_chat("Added to your watchlist.", chat_id=chat_id)
        await notify_group_chat(
            f"<b>New watchlist add</b>\n{_who(user)} --> {labeled_address(bot.w3, address)}",
            chat_id=DEV_GROUP_CHAT_ID,
        )


async def cmd_remove(bot, user, chat_id: int, args: list[str]) -> None:
    if not args:
        await notify_group_chat("Usage: /remove [address]", chat_id=chat_id)
        return

    address = parse_address(args[0])
    if address is None:
        await notify_group_chat("That's not a valid address.", chat_id=chat_id)
        return

    if bot.store.remove_address(user.id, address):
        await notify_group_chat("Removed from your watchlist.", chat_id=chat_id)
    else:
        await notify_group_chat("Not on your watchlist.", chat_id=chat_id)


async def cmd_list(bot, user, chat_id: int, args: list[str]) -> None:
    addresses = bot.store.list_addresses(user.id)
    if not addresses:
        await notify_group_chat("Your watchlist is empty. Use /add [address].", chat_id=chat_id)
        return

    lines = "\n".join(f"- {labeled_address(bot.w3, a)}" for a in addresses)
    await notify_group_chat(f"<b>Your watchlist:</b>\n{lines}", chat_id=chat_id)


HANDLERS = {
    "/start": cmd_start,
    "/help": cmd_help,
    "/add": cmd_add,
    "/remove": cmd_remove,
    "/list": cmd_list,
}

# Shown in Telegram's "/" autocomplete menu (name, description) — no leading slash
COMMANDS = [
    ("add", "Add an address to your watchlist"),
    ("remove", "Remove an address from your watchlist"),
    ("list", "Show your watchlist"),
    ("help", "Show help"),
]
