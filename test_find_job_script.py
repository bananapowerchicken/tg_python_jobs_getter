from telethon import TelegramClient, errors
from datetime import datetime, timedelta
import pytz, asyncio, os
from dotenv import load_dotenv
from tg_python_jobs_getter.utils import channels_list


load_dotenv()

# Замените на ваш API ID и API Hash
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
MSG_AMOUNT_LIMIT = 30

# Инициализация клиента
client = TelegramClient('job_filter_session', API_ID, API_HASH)

# Укажите нужные каналы и ключевое слово
channels = [url.split('/')[-1] for url in channels_list]  # замените на юзернеймы каналов
keyword = 'python'  # ключевое слово для поиска

print("Initializing the client...")


# Функция для обхода всех сообщений в канале
async def process_recent_messages():    
    sent_count = 0
    # Обрабатываем все сообщения в канале
    for channel in channels:
        print(f"Processing messages in channel: {channel}...")
        
        # Получаем все сообщения в канале за последние 24 часа
        async for message in client.iter_messages(channel, limit=MSG_AMOUNT_LIMIT): # last 50 msgs
            # Печатаем информацию о сообщении
            print(f"Processing message ID: {message.id}, Date: {message.date}")
            
            # Получаем текущую дату и время с часовым поясом (например, UTC)
            timezone = pytz.UTC
            time_24_hours_ago = datetime.now(timezone) - timedelta(days=1)

            # Проверяем, если сообщение за последние 24 часа
            if message.date > time_24_hours_ago:
                # Если сообщение содержит ключевое слово, пересылаем его
                if message.message and keyword in message.message.lower():
                    try:
                        await client.send_message('me', message.message)  # Передаем только текст сообщения
                        sent_count += 1
                        print(f"Message {message.id} sent to saved messages.")
                    except errors.FloodWaitError as e:
                        # Лимит Telegram: ждем e.seconds секунд
                        print(f"FloodWaitError: Waiting for {e.seconds} seconds...")
                        await asyncio.sleep(e.seconds)  # Ожидание
                    except Exception as e:
                        print(f"An error occurred: {e}")
                else:
                    print(f"Message {message.id} does not contain the keyword.")
            else:
                print(f"Message {message.id} is older than 24 hours.")
    print(sent_count)

# Запуск клиента
with client:
    print("Script is running...")

    # Обрабатываем последние 24 часа сообщений
    client.loop.run_until_complete(process_recent_messages())
   
    # # Запуск клиента, чтобы оставаться в режиме работы
    # client.run_until_disconnected()