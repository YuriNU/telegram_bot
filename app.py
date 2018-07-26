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

hist=list()
histDict=dict()



def start(bot, update):
    update.message.reply_text('Welcome to Wiki Guide Bot!')


def help(bot, update):
    update.message.reply_text('Type a word to see wiki article')

def back(bot, update):
    chat_id = update.message.chat_id
    if chat_id in histDict:
      h = histDict[chat_id]
      keyboard_buttons=[[h[i]] for i in range(min(len(h),10))]
      reply_markup = ReplyKeyboardMarkup(keyboard_buttons,resize_keyboard=True)
      bot.send_message(chat_id=chat_id, text='История запросов', reply_markup=reply_markup)

def echo(bot, update):
    chat_id = update.message.chat_id
    message_text=update.message.text
                                                   
    url_srsearch='https://ru.wikipedia.org/w/api.php?action=query&list=search&srsearch='+message_text+'&srwhat=text&continue=&format=json'
    response = requests.get(url_srsearch)
    json_data = json.loads(response.text)
    #update.message.reply_text('-----------------------------------')
    page_list=list()
    ref_num=min(len(json_data["query"]["search"]),4)
    for i in range(ref_num):
      page_list.append({'title':json_data["query"]["search"][i]["title"],'pageid':json_data["query"]["search"][i]["pageid"]})
      page_list[i]['url']=get_page_url(page_list[i]['pageid'])
      page_list[i]['snippet']=json_data["query"]["search"][i]["snippet"]
    url_extract='https://ru.wikipedia.org/w/api.php?action=query&prop=extracts&titles='+page_list[0]['title']+'&explaintext&format=json'
    response = requests.get(url_extract)
    json_data = json.loads(response.text)
    extract_keys, extract_values=json_data["query"]["pages"].popitem()
    page_list[0]['snippet']=extract_values["extract"]
    
    addHist(chat_id,page_list[0]['title'])
    
    if(len(histDict[chat_id])>10):
      h = histDict[chat_id]
      h.pop(0)
      histDict[chat_id] = h
    keyboard_buttons=[[page_list[i+1]['title']] for i in range(ref_num-1)]
    reply_markup = ReplyKeyboardMarkup(keyboard_buttons,resize_keyboard=True)
    bot.send_message(chat_id=chat_id, text=page_list[0]['snippet'][:page_list[0]['snippet'].index('.',50)+1], reply_markup=reply_markup)
    update.message.reply_text(page_list[0]['url'])
def addHist(ch, url):
    if ch in histDict:
       histDict[ch].append(url)
    else:
       histDict[ch] = [url]
        
def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))
def get_page_url(page_id):
    page_url_t='https://ru.wikipedia.org/w/api.php?action=query&prop=info&pageids='+str(page_id)+'&inprop=url&format=json'
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
