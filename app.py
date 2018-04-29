import logging
from queue import Queue
from threading import Thread
from telegram import Bot,KeyboardButton,ReplyKeyboardMarkup,ParseMode
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Updater, Filters
import json
import requests



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = '523900080:AAEKgGT4C7M2V4VQ7uWqP7TAB8HzwQJg-jI'





def start(bot, update):
    update.message.reply_text('Welcome to Wiki Guide Bot!')


def help(bot, update):
    update.message.reply_text('Type a word to see wiki article')

def back(bot, update):
    update.message.reply_text('Type a word to see wiki article')

def echo(bot, update):
    chat_id = update.message.chat_id
    message_text=update.message.text
    url_wiki='https://en.wikipedia.org/w/api.php?action=opensearch&search='+message_text+'&limit=1&namespace=0&format=json'
    response = requests.get(url_wiki)
    json_data = json.loads(response.text)
    reference_text=json_data[2]
    refrence_url=json_data[3]
    #update.message.reply_text(reference_text)
    #update.message.reply_text(refrence_url)
    #update.message.reply_text(json_data)
    
    url_srsearch='https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch='+message_text+'&srwhat=text&continue=&format=json'
    response = requests.get(url_srsearch)
    json_data = json.loads(response.text)
    #update.message.reply_text('-----------------------------------')
    page_list=list()
    ref_num=min(len(json_data["query"]["search"]),4)
    for i in range(ref_num):
      page_list.append({'title':json_data["query"]["search"][i]["title"],'pageid':json_data["query"]["search"][i]["pageid"]})
      page_list[i]['url']=get_page_url(page_list[i]['pageid'])
      page_list[i]['snippet']=json_data["query"]["search"][i]["snippet"]
      
    reply_markup = ReplyKeyboardMarkup([[page_list[i+1]['title']] for i in range(ref_num-1)],resize_keyboard=True)
    bot.send_message(chat_id=chat_id, text=page_list[0]['snippet'], reply_markup=reply_markup)
    update.message.reply_text(page_list[0]['url'])
    
def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))
def get_page_url(page_id):
    page_url_t='https://en.wikipedia.org/w/api.php?action=query&prop=info&pageids='+str(page_id)+'&inprop=url&format=json'
    response_t = requests.get(page_url_t)
    json_data_t = json.loads(response_t.text)
    return json_data_t["query"]["pages"][str(page_id)]["fullurl"]
# Write your handlers here


def setup(webhook_url=None):
    """If webhook_url is not passed, run with long-polling."""
    logging.basicConfig(level=logging.WARNING)
    if webhook_url:
        bot = Bot(TOKEN)
        update_queue = Queue()
        dp = Dispatcher(bot, update_queue)
    else:
        updater = Updater(TOKEN, request_kwargs={'read_timeout': 6, 'connect_timeout': 7})
        bot = updater.bot
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", help))
        dp.add_handler(CommandHandler("back", back))
       

        # on noncommand i.e message - echo the message on Telegram
        dp.add_handler(MessageHandler(Filters.text, echo))

        # log all errors
        dp.add_error_handler(error)
    # Add your handlers here
    if webhook_url:
        bot.set_webhook(webhook_url=webhook_url)
        thread = Thread(target=dp.start, name='dispatcher')
        thread.start()
        return update_queue, bot
    else:
        try:
          bot.set_webhook()  # Delete webhook
          updater.start_polling()
          updater.idle()
        except Exception:
          print("Could not convert data to an integer.")



if __name__ == '__main__':
    setup()
