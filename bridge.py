import asyncio
from telegram import Bot

TOKEN = "8560410689:AAHvS9c4LunVrB-aX9gIEIquehUWwiLSVFg"

async def send_treasure():
    async with Bot(token=TOKEN) as bot:
        me = await bot.get_me()
        print(f"تم الاتصال بنجاح بالبوت: {me.first_name} (@{me.username})")

if __name__ == "__main__":
    asyncio.run(send_treasure())
