import logging
from queue import Queue
from threading import Thread
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Updater, Filters
import json
import requests



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = '523900080:AAEKgGT4C7M2V4VQ7uWqP7TAB8HzwQJg-jI'





def start(bot, update):
    update.message.reply_text('welcome to wiki guide bot!')


def help(bot, update):
    update.message.reply_text('help message')


def echo(bot, update):
    #response = urllib2.urlopen('https://en.wikipedia.org/w/api.php?action=opensearch&search=president&limit=1&namespace=0&format=json')
    url_wiki='https://en.wikipedia.org/w/api.php?action=opensearch&search='+update.message.text+'&limit=1&namespace=0&format=json'
    response = requests.get(url_wiki)
    json_data = json.loads(response.text)
    reference_text=json_data[2,0]
    refrence_url=json_data[3,0]
    update.message.reply_text(reference_text)
    update.message.reply_text(refrence_url)
    update.message.reply_text(json_data)

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))

# Write your handlers here


def setup(webhook_url=None):
    """If webhook_url is not passed, run with long-polling."""
    logging.basicConfig(level=logging.WARNING)
    if webhook_url:
        bot = Bot(TOKEN)
        update_queue = Queue()
        dp = Dispatcher(bot, update_queue)
    else:
        updater = Updater(TOKEN)
        bot = updater.bot
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", help))

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
        bot.set_webhook()  # Delete webhook
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    setup()
