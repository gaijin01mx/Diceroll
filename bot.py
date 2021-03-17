from telegram.ext import *
import logging
import Constants as Keys
from Roll import Roll, WodRoll


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Bienvenido al Bot de Wod. Escriba /roll NdF, ex. 3d10 o /wod N D")


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Aun no implemento el menu')


def echo(context, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error_command(bot, update, error):
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

    bot.send_message(chat_id=update.message.chat_id, text="Rolling {} : {}".format(args, roll.roll_dice()))


def wod_roll(bot, update, args):
    """"
    World of Destruction Rolls
    """
    args = ' '.join(args).upper()

    roll = WodRoll(args)
    n, d, result, message = roll.roll_dice()

    bot.send_message(chat_id=update.message.chat_id, text="Lanzando {}d10 : Dificultad de {} \n"
                                                          "Result: {} => {}".format(n, d, result, message))


def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Lo siento no entendi el comando.")


def main():
    print('Running bot... ')
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(Keys.API_KEY, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("xp", xp))
    dp.add_handler(CommandHandler("roll", roll))
    dp.add_handler(CommandHandler("wod", wod_roll))
    dp.add_handler(CommandHandler("armor", armor))
    dp.add_handler(CommandHandler("melee", melee))
    dp.add_handler(CommandHandler("weapons", weapons))

    dp.add_handler(MessageHandler(Filters.command, unknown))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
