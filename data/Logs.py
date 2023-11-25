bot_log_channel = None

async def SendLog(bot, log_text):
    if bot_log_channel is None:
        print("Log channel is not set.")
        return
    await bot.get_channel(bot_log_channel).send(log_text) 