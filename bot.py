import sys
import time
import re
import random
import traceback
import unicodedata
import logging
from telegram import Update, ParseMode
from telegram.ext import *
from codecs import encode, decode
from datetime import datetime
from ast import literal_eval
import Constants as Keys

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Bienvenido al Bot oficial de Wod Lobo. Para hacer su tirada escriba /roll NdF, ex. 3d10")

    
def help(update: Update, context: CallbackContext):
    username = update.message.from_user.username if update.message.from_user.username else update.message.from_user.first_name
    help_file = open('help.html', 'r')
    response = (help_file.read())
    help_file.close()
    logging.info(f'@{username} | /help')
    job = context.job
    context.bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    
    
def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)
    
    
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def xp(bot, update):
    bot.send_photo(chat_id=update.message.chat_id, photo=open('img/xp-1.png', 'rb'))


def armor(bot, update):
    bot.send_photo(chat_id=update.message.chat_id, photo=open('img/Tabla-de-armadura.png', 'rb'))


def melee(bot, update):
    bot.send_photo(chat_id=update.message.chat_id, photo=open('img/Tabla-de-armas-cuerpo-a-cuerpo.png', 'rb'))


def weapons(bot, update):
    bot.send_photo(chat_id=update.message.chat_id, photo=open('img/tabla-de-armas-de-largo-alcance.png', 'rb'))


def roll(bot, update, args):
    args = args[0]
    roll = Roll(args)

    bot.send_message (chat_id=update.message.chat_id, text="Rolling {} : {}".format(args, roll.roll_dice()))


def wod_roll(bot, update, args):
    """"
    World of Destruction Rolls
    """
    args = ' '.join(args).upper()

    roll = WodRoll(args)
    n, d, result, message = roll.roll_dice()

    bot.send_message (chat_id=update.message.chat_id, text="Rolling {}d10 : Dificuldade {} \n"
                                                           "Result: {} => {}".format(n,d,result, message ))    
    
   
def main():
    updater = Updater(Keys.API_KEY, use_context=True)
    dispatcher = updater.dispatcher

# on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("xp", xp))
    dispatcher.add_handler(CommandHandler("armor", armor))
    dispatcher.add_handler(CommandHandler("melee", melee))
    dispatcher.add_handler(CommandHandler("weapons", weapons))

# log all errors
    dispatcher.add_error_handler(error)
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))
    dispatcher.add_handler(MessageHandler(Filters.text, echo))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

