import requests
import os
import time
from telegram import Bot
from bs4 import BeautifulSoup
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

bot = Bot(token=TELEGRAM_BOT_TOKEN)

previous_gas_price = None

async def fetch_gas_price():
    global previous_gas_price

    try:
        url = 'https://etherscan.io/gastracker'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        print("Response code:", response.status_code)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            gas_price_low = int(soup.find(id='spanLowPrice').text)
            gas_price_avg = int(soup.find(id='spanAvgPrice').text)
            gas_price_high = int(soup.find(id='spanHighPrice').text)

            print("Fetched gas prices:", gas_price_low, gas_price_avg, gas_price_high)

            if previous_gas_price is None or gas_price_low != previous_gas_price:
                previous_gas_price = gas_price_low
                
                if gas_price_low <= 2:
                    multiline_message = "Вперед воркать, газ по цене песка!\n"\
                    f"LOW: {gas_price_low}\n"\
                    f"AVERAGE: {gas_price_avg}\n"\
                    f"HIGH: {gas_price_high}"\
                    
                    await bot.send_message(chat_id=CHAT_ID, text=multiline_message)
                    print("Message sent:", multiline_message)
                else:
                    print("Low gas price is higher than 2, no message sent.")
            else:
                print("Gas price hasn't changed since last check, no message sent.")
        else:
            print("Ошибка при получении данных")
    except Exception as e:
        print(f"Ошибка: {e}")

async def check_gas_price_and_notify():
    print("Checking gas price...")
    await fetch_gas_price()

if __name__ == '__main__':
    print("Bot started. Waiting for scheduled tasks...")

    timezone = pytz.utc
    scheduler = AsyncIOScheduler(timezone=timezone)
    scheduler.add_job(check_gas_price_and_notify, 'interval', seconds=20)
    scheduler.start()

    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass