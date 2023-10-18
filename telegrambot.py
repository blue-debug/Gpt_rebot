import os
import json, time
import openai
import logging, threading

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackContext

with open("config.json", "r") as f: config = json.load(f)

openai.api_key = os.environ["OPENAI_API_KEY"] = config["openai_api_key"]

# if not os.path.exists("log"):
#     os.makedirs("log")

# if not os.path.exists("bot_running.log"):
#     os.rmdir("bot_running.log")

# logging module
logger = logging.getLogger("chatgpt_logger")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("bot_running.log", mode = "a")
file_handler.setLevel(logging.DEBUG)
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)


text_list = []

def limit_list_size(max_size = 4000):
    global text_list
    global config

    with open("config.json", "r") as f: config = json.load(f)

    while True:
        serialized_list = json.dumps(text_list).split()
        if len(serialized_list) > max_size:
            limited_list = []
            current_size = 0
            for sub_list in text_list:
                serialized_sub_list = json.dumps(sub_list).split()
                if current_size + len(serialized_sub_list) > max_size:
                    break
                limited_list.append(sub_list)
                current_size += len(serialized_sub_list)
            
            limited_list = limited_list[:-1]
            while len(json.dumps(limited_list).split()) > max_size:
                limited_list = limited_list[:-1]
            
            text_list = limited_list
        
        # with open("log.txt", "a") as f:
        #     f.write("asd\n")
        time.sleep(60)
    

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(update)
    await context.bot.send_message(chat_id = update.effective_chat.id, text = "I'm not a bot, please don't talk to me!")

async def clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global text_list
    text_list = []
    await context.bot.send_message(chat_id = update.effective_chat.id, text = "clean successfully")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id = update.effective_chat.id, text = f'token: {len(json.dumps(text_list).split())}\n' + str(text_list))
    except:
        await context.bot.send_message(chat_id = update.effective_chat.id, text = f'token: {len(json.dumps(text_list).split())}')

async def shell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if (update.effective_chat.id in config["own_id"]):
            bash = update.message.text.split("/shell")[1]
            logger.info(bash)
            output = os.popen(bash).read()
            if not output: output = "invalid command"
    except:
        output = "invalid command"
    finally:
        await context.bot.send_message(chat_id = update.effective_chat.id, text = output)

async def image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    requirment = update.message.text.split("/image")[1]
    logger.info("Image: %s", requirment)
    response = openai.Image.create(
        prompt = requirment,
        n = 1,
        size = "256x256" # 256x256 512x512 1024x1024
    )
    image_url = response['data'][0]['url']
    logger.info(image_url)
    await context.bot.send_photo(chat_id = update.effective_chat.id, photo = image_url)

# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

async def chatgpt_response(text: str) -> str:
    text_list.append({"role": "user", "content": text})
    response = openai.ChatCompletion.create(model = "gpt-3.5-turbo", messages = text_list)
    return response.choices[0]['message']['content']


async def chat(update: Update, context: CallbackContext) -> None:
    current_text = update.message.text
    logger.info("Chat: %s", current_text)
    gpt_response = await chatgpt_response(update.message.text)
    text_list.append({"role": "assistant", "content": gpt_response})
    logger.info(gpt_response)
    # update.message.reply_text(gpt_response)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=gpt_response)


if __name__ == '__main__':
    application = ApplicationBuilder().token(config["bot_api_key"]).build()
    
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), chat)
    clean_handler = CommandHandler('clean', clean)
    status_handler = CommandHandler('status', status)
    shell_handler = CommandHandler('shell', shell)
    image_handler = CommandHandler('image', image)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(clean_handler)
    application.add_handler(status_handler)
    application.add_handler(shell_handler)
    application.add_handler(image_handler)

    # async def limit_task():
    #     while True:
    #         await limit_list_size(4000)
    #         await asyncio.sleep(60)

    # async def main():
    #     task = asyncio.create_task(limit_task())
    #     await asyncio.gather(task)

    # asyncio.run(main())

    thread = threading.Thread(target = limit_list_size, args = (4000,))
    thread.start()

    logger.info("Bot starting...")

    application.run_polling()

