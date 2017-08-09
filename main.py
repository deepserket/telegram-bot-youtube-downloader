import logging

from telegram import InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler, MessageHandler, Filters

from vid_utils import Video

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

video = None

def get_format(bot, update):
    logger.info(update.message.text) # "history"
    global video
    video = Video(update.message.text, update.message.chat_id)

    reply_markup = InlineKeyboardMarkup(video.keyboard)
    update.message.reply_text('Choose format:', reply_markup=reply_markup)


def download_choosen_format(bot, update):
    query = update.callback_query

    video.download(query.data)
    bot.edit_message_text(text="Downloading...",
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)

    with video.send() as files:
        for f in files:
            bot.send_document(chat_id=query.message.chat_id, document=open(f, 'rb'))


updater = Updater(token=YOUR_TOKEN)

updater.dispatcher.add_handler(MessageHandler(Filters.text, get_format))
updater.dispatcher.add_handler(CallbackQueryHandler(download_choosen_format))

# Start the Bot
updater.start_polling()
updater.idle()
