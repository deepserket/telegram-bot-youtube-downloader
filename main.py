import logging

from telegram import InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler, MessageHandler, Filters

from vid_utils import Video, BadLink

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def get_format(bot, update):
    logger.info("from {}: {}".format(update.message.chat_id, update.message.text)) # "history"

    try:
        video = Video(update.message.text, init_keyboard=True)
    except BadLink:
        update.message.reply_text("Bad link")
    else:
        reply_markup = InlineKeyboardMarkup(video.keyboard)
        update.message.reply_text('Choose format:', reply_markup=reply_markup)


def download_choosen_format(bot, update):
    query = update.callback_query
    resolution_code, link = query.data.split(' ', 1)
    
    bot.edit_message_text(text="Downloading...",
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    
    video = Video(link)
    video.download(resolution_code)
    
    with video.send() as files:
        for f in files:
            bot.send_document(chat_id=query.message.chat_id, document=open(f, 'rb'))


updater = Updater(token=YOUR_TOKEN)

updater.dispatcher.add_handler(MessageHandler(Filters.text, get_format))
updater.dispatcher.add_handler(CallbackQueryHandler(download_choosen_format))


updater.start_polling()
updater.idle()
