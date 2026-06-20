from tinybot import notify_group_chat


async def post_event(bot, text: str, owner: str | None = None) -> None:
    """Post an event to the public group, and DM it to anyone watching `owner`."""
    await notify_group_chat(text)
    if owner is not None:
        for chat_id in bot.store.watchers_of(owner):
            await notify_group_chat(text, chat_id=chat_id)
