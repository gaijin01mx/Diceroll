import sys
import time
import re
import random
import traceback
import unicodedata
import logging
from telegram import Update, ParseMode, TelegramError
from time import sleep
from telegram.ext import *
from telegram.ext.dispatcher import run_async
from codecs import encode, decode
from datetime import datetime
from ast import literal_eval
from config import BOTNAME
import Constants as Keys


help_text = (
    "Le da la bienvenida a cualquiera que entre a este chat"
    "Por default solo la persona que invito al bot al "
    "grupo puede cambiar los atributos del mismo.\nCommands:\n\n"
    "/welcome - Establece un mensaje de Bienvenida\n"
    "/goodbye - Establece un mensaje de despedida\n"
    "/disable\\_goodbye - Desactiva el mensaje de despedida\n"
    "/lock - Solo la persona que invitó al bot puede cambiar el mensaje\n"
    "/unlock - Todos pueden cambiar el mensaje\n"
    '/quiet - Desactiva "Lo siento solo la persona que..." '
    "& help messages\n"
    '/unquiet - Activa "Lo siento, solo la persona que..." '
    "& help messages\n\n"
    "Puedes usar _$username_ y _$title_ como placeholders al programar"
    " mensajes. [HTML formatting]"
    "(https://core.telegram.org/bots/api#formatting-options) "
    "tambien esta soportado.\n"
)

"""
Create database object
Database schema:
<chat_id> -> welcome message
<chat_id>_bye -> goodbye message
<chat_id>_adm -> user id of the user who invited the bot
<chat_id>_lck -> boolean if the bot is locked or unlocked
<chat_id>_quiet -> boolean if the bot is quieted
chats -> list of chat ids where the bot has received messages in.
"""


ladder = {
    8: 'Legendario',
    7: 'Epico',
    6: 'Fantástico',
    5: 'Soberbio',
    4: 'Grandioso',
    3: 'Bueno',
    2: 'Regular',
    1: 'Promedio',
    0: 'Mediocre',
    -1: 'Pobre',
    -2: 'Terrible'
}


def get_ladder(result):
    if result > 8:
        return 'Mas alla de legendario'
    elif result < -2:
        return 'Terrible'
    else:
        return ladder[result]


fate_options = {
    -1: '[-]',
    0: '[  ]',
    1: '[+]'
}

def rf(update: Update, context: CallbackContext):
    logging.debug(context.args)
    if len(context.args) > 0:
        context.args[0] = '4df+' + str(context.args[0])
    else:
        context.args = ['4df']
    process(update, context)


def process(update: Update, context: CallbackContext):
    username = update.message.from_user.username if update.message.from_user.username else update.message.from_user.first_name
    equation = context.args[0].strip() if len(context.args) > 0 else False
    equation_list = re.findall(r'(\w+!?>?\d*)([+*/()-]?)', equation)
    comment = ' ' + ' '.join(context.args[1:]) if len(context.args) > 1 else ''
    space = ''
    dice_num = None
    original_dice_num = None
    is_fate = False
    use_ladder = False
    nat20text = ''
    high_low_helper = ''
    if '2d20' in equation.lower() and not ('2d20h' in equation.lower() or '2d20l' in equation.lower()):
        high_low_helper = 'Obten el valor mas bajo y alte en una tirada usando H and L.\r\nEscribe <code>/help</code> para mas info.\r\n\r\n'
    result = {
        'visual': [],
        'equation': [],
        'total': ''
    }

    try:
        for pair in equation_list:
            logging.debug(f"pair: {pair}")
            pair = [i for i in pair if i]
            for item in pair:
                logging.debug(f"item: {item}")
                if item and len(item) > 1 and any(d in item for d in ['d', 'D']):
                    dice = re.search(r'(\d*)d([0-9f]+)([!hl])?', item.lower())
                    dice_num = int(dice.group(1)) if dice.group(1) else 1
                    original_dice_num = dice_num
                    if dice_num > 1000:
                        raise Exception('La cantidad máxima de dados para tirar es de 1000')
                    sides = dice.group(2)
                    space = ' '
                    result['visual'].append(space + '(')
                    result['equation'].append('(')
                    fate_dice = ''
                    current_die_results = ''
                    current_visual_results = ''
                    plus = ''
                    explode = False
                    highest = False
                    lowest = False
                    if dice.group(3) and dice.group(3)[0] == '!' and int(dice.group(2)) > 1:
                        explode = True
                    elif dice.group(3) and dice.group(3)[0] in ['h', 'H']:
                        highest = True
                    elif dice.group(3) and dice.group(3)[0] in ['l', 'L']:
                        lowest = True

                    random_start_num = 1
                    if sides in ['f', 'F']:
                        is_fate = True
                        use_ladder = True
                        sides = 1
                        random_start_num = -1
                    else:
                        sides = int(sides)

                    while dice_num > 0:

                        last_roll = random.randint(random_start_num, sides)
                        visual_last_roll = plus + str(last_roll)
                        if is_fate:
                            visual_last_roll = fate_options[last_roll] + ' '
                        current_visual_results += visual_last_roll

                        if (highest or lowest) and current_die_results:
                            # print(current_die_results)
                            if highest:
                                if last_roll > int(current_die_results):
                                    current_die_results = str(last_roll)
                            else:  # lowest
                                if last_roll < int(current_die_results):
                                    current_die_results = str(last_roll)
                        else:
                            current_die_results += plus + str(last_roll)

                        if not (explode and last_roll == sides):
                            dice_num -= 1

                        if len(plus) == 0:
                            # Adds all results to result unless it is the first one
                            plus = ' + '

                        if sides == 20 and last_roll == 20 and original_dice_num < 3 and '20' in current_die_results:
                            nat20text = '    #Natural20'

                    if is_fate:
                        is_fate = False
                    result['visual'].append(current_visual_results)
                    result['equation'].append(current_die_results)
                    result['visual'].append(')')
                    result['equation'].append(')')
                    if highest or lowest:
                        result['visual'].append(dice.group(3)[0])
                else:
                    if item and (item in ['+', '-', '/', '*', ')', '('] or int(item)):
                        result['visual'].append(' ')
                        result['visual'].append(item)
                        result['equation'].append(item)

        result['total'] = str(''.join(result['equation'])).replace(" ", "")
        if bool(re.match('^[0-9+*/ ()-]+$', result['total'])):
            result['total'] = eval(result['total'])
        else:
            raise Exception('La solicitud no es valida, checa tu sintaxis')

        if use_ladder:
            # Set if final result is positive or negative
            sign = '+' if result['total'] > -1 else ''
            ladder_result = get_ladder(result['total'])
            result['total'] = sign + str(result['total']) + ' ' + ladder_result

        # Only show part of visual equation if bigger than 300 characters
        result['visual'] = ''.join(result['visual'])
        if len(result['visual']) > 275:
            result['visual'] = result['visual'][0:275] + ' . . . )'

        logging.info(f'@{username} | ' + ' '.join(context.args) + ' = ' + ''.join(result['equation']) + ' = ' + str(
            result['total']) + nat20text)
        response = (
            f'{high_low_helper}@{username} tiró<b>{comment}</b>:\r\n {result["visual"]} =\r\n<b>{str(result["total"])}</b>{nat20text}')
        error = ''

    except Exception as e:
        response = f'@{username}: <b>Ecuación invalida!</b>\r\n'
        if dice_num and dice_num > 1000:
            response += str(e) + '.\r\n'
        response += ('Por favor usa <a href="https://en.wikipedia.org/wiki/Dice_notation"> la notación de dados</a>.\r\n' +
                     'Por ejemplo: <code>3d6</code>, o <code>1d20+5</code>, o <code>d12</code>\r\n\r\n' +
                     'Para mas información, escribe <code>/help</code>'
                     )
        error = traceback.format_exc().replace('\r', '').replace('\n', '; ')
        logging.warning(f'@{username} | /r {equation} | RESPONSE: Ecuación invalida |\r\n{error}')

    context.bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode=ParseMode.HTML)


def help(update: Update, context: CallbackContext):
    username = update.message.from_user.username if update.message.from_user.username else update.message.from_user.first_name
    help_file = open('help.html', 'r')
    response = (help_file.read())
    help_file.close()
    logging.info(f'@{username} | /help')
    job = context.job
    context.bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode=ParseMode.HTML,
                             disable_web_page_preview=True)

def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Bienvenido al Bot oficial de Wod Lobo. Para hacer su tirada escriba /roll NdF, ex. 3d10")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def xp(bot, update):
    bot.send_photo(chat_id=update.message.chat_id, photo=open('xp-1.png', 'rb'))


def armor(bot, update):
    bot.send_photo(chat_id=update.message.chat_id, photo=open('img/Tabla-de-armadura.png', 'rb'))


def melee(bot, update):
    bot.send_photo(chat_id=update.message.chat_id, photo=open('Tabla-de-armas-cuerpo-a-cuerpo.png', 'rb'))


def weapons(bot, update):
    bot.send_photo(chat_id=update.message.chat_id, photo=open('img/tabla-de-armas-de-largo-alcance.png', 'rb'))


formatter = logging.Formatter('====> %(asctime)s | %(name)s | %(levelname)s | %(message)s')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
file_handler = logging.FileHandler('roll.log')
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

logger = logging.basicConfig(
    handlers=[stream_handler, file_handler],
    level=logging.DEBUG,
)

# Create database object
db = pickledb.load("bot.db", True)

if not db.get("chats"):
    db.set("chats", [])

# Set up logging
root = logging.getLogger()
root.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@run_async
def send_async(context, *args, **kwargs):
    context.bot.send_message(*args, **kwargs)


def check(update, context, override_lock=None):
    """
    Perform some checks on the update. If checks were successful, returns True,
    else sends an error message to the chat and returns False.
    """

    chat_id = update.message.chat_id
    chat_str = str(chat_id)

    if chat_id > 0:
        send_async(
            context, chat_id=chat_id, text="Por favor añademe a un prupo primero!",
        )
        return False

    locked = override_lock if override_lock is not None else db.get(chat_str + "_lck")

    if locked and db.get(chat_str + "_adm") != update.message.from_user.id:
        if not db.get(chat_str + "_quiet"):
            send_async(
                context,
                chat_id=chat_id,
                text="Lo siento, solo la persona que me invito puede hacer eso!.",
            )
        return False

    return True


# Welcome a user to the chat
def welcome(update, context, new_member):
    """ Welcomes a user to the chat """

    message = update.message
    chat_id = message.chat.id
    logger.info(
        "%s joined to chat %d (%s)",
        escape(new_member.first_name),
        chat_id,
        escape(message.chat.title),
    )

    # Pull the custom message for this chat from the database
    text = db.get(str(chat_id))

    # Use default message if there's no custom one set
    if text is None:
        text = "Hola $username! Bienvenido a $title 😊"

    # Replace placeholders and send message
    text = text.replace("$username", new_member.first_name)
    text = text.replace("$title", message.chat.title)
    send_async(context, chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)


# Welcome a user to the chat
def goodbye(update, context):
    """ Sends goodbye message when a user left the chat """

    message = update.message
    chat_id = message.chat.id
    logger.info(
        "%s left chat %d (%s)",
        escape(message.left_chat_member.first_name),
        chat_id,
        escape(message.chat.title),
    )

    # Pull the custom message for this chat from the database
    text = db.get(str(chat_id) + "_bye")

    # Goodbye was disabled
    if text is False:
        return

    # Use default message if there's no custom one set
    if text is None:
        text = "Adios $username!, nadie te extrañara"

    # Replace placeholders and send message
    text = text.replace("$username", message.left_chat_member.first_name)
    text = text.replace("$title", message.chat.title)
    send_async(context, chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)


# Introduce the bot to a chat its been added to
def introduce(update, context):
    """
    Introduces the bot to a chat its been added to and saves the user id of the
    user who invited us.
    """

    chat_id = update.message.chat.id
    invited = update.message.from_user.id

    logger.info(
        "Invitado por %s al chat %d (%s)", invited, chat_id, update.message.chat.title,
    )

    db.set(str(chat_id) + "_adm", invited)
    db.set(str(chat_id) + "_lck", True)

    text = (
        f"Hello {update.message.chat.title}! "
        "I will now greet anyone who joins this chat with a "
        "nice message 😊 \nCheck the /help command for more info!"
    )
    send_async(context, chat_id=chat_id, text=text)


# Print help text
def botwelc(update, context):
    """ Prints help text """

    chat_id = update.message.chat.id
    chat_str = str(chat_id)
    if (
        not db.get(chat_str + "_quiet")
        or db.get(chat_str + "_adm") == update.message.from_user.id
    ):
        send_async(
            context,
            chat_id=chat_id,
            text=help_text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )


# Set custom message
def set_welcome(update, context):
    """ Sets custom welcome message """

    chat_id = update.message.chat.id

    # Check admin privilege and group context
    if not check(update, context):
        return

    # Split message into words and remove mentions of the bot
    message = update.message.text.partition(" ")[2]

    # Only continue if there's a message
    if not message:
        send_async(
            context,
            chat_id=chat_id,
            text="You need to send a message, too! For example:\n"
            "<code>/welcome Hello $username, welcome to "
            "$title!</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    # Put message into database
    db.set(str(chat_id), message)

    send_async(context, chat_id=chat_id, text="Entendido!")


# Set custom message
def set_goodbye(update, context):
    """ Enables and sets custom goodbye message """

    chat_id = update.message.chat.id

    # Check admin privilege and group context
    if not check(update, context):
        return

    # Split message into words and remove mentions of the bot
    message = update.message.text.partition(" ")[2]

    # Only continue if there's a message
    if not message:
        send_async(
            context,
            chat_id=chat_id,
            text="You need to send a message, too! For example:\n"
            "<code>/goodbye Goodbye, $username!</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    # Put message into database
    db.set(str(chat_id) + "_bye", message)

    send_async(context, chat_id=chat_id, text="Entendido!")


def disable_goodbye(update, context):
    """ Disables the goodbye message """

    chat_id = update.message.chat.id

    # Check admin privilege and group context
    if not check(update, context):
        return

    # Disable goodbye message
    db.set(str(chat_id) + "_bye", False)

    send_async(context, chat_id=chat_id, text="Entendido!")


def lock(update, context):
    """ Locks the chat, so only the invitee can change settings """

    chat_id = update.message.chat.id

    # Check admin privilege and group context
    if not check(update, context, override_lock=True):
        return

    # Lock the bot for this chat
    db.set(str(chat_id) + "_lck", True)

    send_async(context, chat_id=chat_id, text="Entendido!")


def quiet(update, context):
    """ Quiets the chat, so no error messages will be sent """

    chat_id = update.message.chat.id

    # Check admin privilege and group context
    if not check(update, context, override_lock=True):
        return

    # Lock the bot for this chat
    db.set(str(chat_id) + "_quiet", True)

    send_async(context, chat_id=chat_id, text="Entendido!")


def unquiet(update, context):
    """ Unquiets the chat """

    chat_id = update.message.chat.id

    # Check admin privilege and group context
    if not check(update, context, override_lock=True):
        return

    # Lock the bot for this chat
    db.set(str(chat_id) + "_quiet", False)

    send_async(context, chat_id=chat_id, text="Entendido!")


def unlock(update, context):
    """ Unlocks the chat, so everyone can change settings """

    chat_id = update.message.chat.id

    # Check admin privilege and group context
    if not check(update, context):
        return

    # Unlock the bot for this chat
    db.set(str(chat_id) + "_lck", False)

    send_async(context, chat_id=chat_id, text="Entendido!")


def empty_message(update, context):
    """
    Empty messages could be status messages, so we check them if there is a new
    group member, someone left the chat or if the bot has been added somewhere.
    """

    # Keep chatlist
    chats = db.get("chats")

    if update.message.chat.id not in chats:
        chats.append(update.message.chat.id)
        db.set("chats", chats)
        logger.info("Me han añadido a %d chats" % len(chats))

    if update.message.new_chat_members:
        for new_member in update.message.new_chat_members:
            # Bot was added to a group chat
            if new_member.username == BOTNAME:
                return introduce(update, context)
            # Another user joined the chat
            else:
                return welcome(update, context, new_member)

    # Someone left the chat
    elif update.message.left_chat_member is not None:
        if update.message.left_chat_member.username != BOTNAME:
            return goodbye(update, context)


def error(update, context, **kwargs):
    """ Error handling """
    error = context.error

    try:
        if isinstance(error, TelegramError) and (
            error.message == "Unauthorized"
            or error.message == "Have no rights to send a message"
            or "PEER_ID_INVALID" in error.message
        ):
            chats = db.get("chats")
            chats.remove(update.message.chat_id)
            db.set("chats", chats)
            logger.info("Removed chat_id %s from chat list" % update.message.chat_id)
        else:
            logger.error("An error (%s) occurred: %s" % (type(error), error.message))
    except:
        pass
            
            
            
print('Corriendo el bot... ')
# Create the EventHandler and pass it your bot's token.
updater = Updater(Keys.API_KEY, use_context=True)
dispatcher = updater.dispatcher



# on different commands - answer in Telegram
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("botwelc", botwelc))
dispatcher.add_handler(CommandHandler("help", help))
dispatcher.add_handler(CommandHandler("xp", xp))
dispatcher.add_handler(CommandHandler("armor", armor))
dispatcher.add_handler(CommandHandler("melee", melee))
dispatcher.add_handler(CommandHandler("weapons", weapons))
dispatcher.add_handler(CommandHandler("welcome", set_welcome))
dispatcher.add_handler(CommandHandler("goodbye", set_goodbye))
dispatcher.add_handler(CommandHandler("disable_goodbye", disable_goodbye))
dispatcher.add_handler(CommandHandler("lock", lock))
dispatcher.add_handler(CommandHandler("unlock", unlock))
dispatcher.add_handler(CommandHandler("quiet", quiet))
dispatcher.add_handler(CommandHandler("unquiet", unquiet))



# log all errors
dispatcher.add_error_handler(error)

roll_handler = CommandHandler(['roll', 'r'], process, pass_args=True)
dispatcher.add_handler(roll_handler)

roll_handler = CommandHandler('rf', rf, pass_args=True)
dispatcher.add_handler(roll_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

updater.start_polling()
