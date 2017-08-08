import os
import logging
from glob import glob
from subprocess import Popen, PIPE

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler,
                    MessageHandler, Filters)

from vid_utils import check_dimension

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

#TODO I don't like these global vars...
formats = [] # aviable format of the video
link = '' #link of the video

def generate_keyboard(l):
    """ return a keyboard fom list l """
    kb = []

    for code, extension, resolution in l:
        kb.append([InlineKeyboardButton("{0}, {1}".format(extension, resolution),
                                       callback_data=code)])
    return kb

def get_format(bot, update):
    global link
    link = update.message.text # saving link in global var
    formats[:] = [] # remove old formats

    for f in glob('*.mp4*') + glob('*.webm*'): # with glob it is not possible check multiple extension in one regex
        os.remove(f) # remove old video(s)

    try:
        """
        p = subprocess.Popen("youtube-dl -F {}".format(update.message.text), shell=True, stdout=subprocess.PIPE) # this line can be very dangerous, there is a serious command-injection problem
        p = p.communicate()
        """
        cmd = "youtube-dl -F {}".format(update.message.text) # this line can be very dangerous, there is a serious command-injection problem
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        p = p.communicate()
        it = iter(str(p[0], 'utf-8').split('\n'))

        while not "code  extension" in next(it): # Remove garbage lines, i need only the formats
            pass

        while True: # save the formats in the formats list
            try:
                line = next(it)
                if not line: # the last line usually is empty...
                    raise StopIteration
                if "video only" in line: # video without audio... why?
                    continue
            except StopIteration:
                break
            else:
                format_code, extension, resolution, *_ = line.strip().split()
                formats.append([format_code, extension, resolution])

    except Exception as e:
        bot.sendMessage(chat_id=update.message.chat_id, text='Error: {}'.format(e))
        logger.info(e)
        raise e

    else:
        reply_markup = InlineKeyboardMarkup(generate_keyboard(formats))
        update.message.reply_text('Choose format:', reply_markup=reply_markup)


def download_choosen_format(bot, update):
    query = update.callback_query

    bot.edit_message_text(text="Downloading...",
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)

    os.system("youtube-dl -f {0} {1}".format(query.data, link))

    for f in glob('*.mp4*') + glob('*.webm*'):
        check_dimension(f)
        break # check first file

    for f in glob('*.mp4*') + glob('*.webm*'): # send document(s)
        bot.send_document(chat_id=query.message.chat_id, document=open(f, 'rb'))


updater = Updater(token=INSERT_YOUR_TOKEN_HERE)

updater.dispatcher.add_handler(MessageHandler(Filters.text, get_format))
updater.dispatcher.add_handler(CallbackQueryHandler(download_choosen_format))

# Start the Bot
updater.start_polling()
updater.idle()
