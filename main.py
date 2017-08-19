import logging
from time import sleep

from telegram import InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler, MessageHandler, Filters

from vid_utils import Video, VideoQueue, BadLink

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

VIDEOS = VideoQueue()

def get_format(bot, update):
    logger.info("from {}: {}".format(update.message.chat_id, update.message.text)) # "history"

    try:
        video = Video(update.message.text, update.message.chat_id)
    except BadLink:
        update.message.reply_text("Bad link")
    else:
        for i, v in enumerate(VIDEOS):
            if v.chat_id == video.chat_id:
                VIDEOS[i] = video # remove old video not downloaded...
                break
        else:
            VIDEOS.append(video)
        
        reply_markup = InlineKeyboardMarkup(video.keyboard)
        update.message.reply_text('Choose format:', reply_markup=reply_markup)


def download_choosen_format(bot, update):
    query = update.callback_query
    bot.edit_message_text(text="Downloading...",
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)

    while VIDEOS.lock: sleep(1) # finish old download

    VIDEOS.lock = True # maybe we can use a contextmanager?

    for i, video in enumerate(VIDEOS):
        if video.chat_id == query.message.chat_id:
            VIDEOS.pop(i)
            video.download(query.data)

    with video.send() as files:
        for f in files:
            bot.send_document(chat_id=query.message.chat_id, document=open(f, 'rb'))

    VIDEOS.lock = False


updater = Updater(token=YOUR_TOKEN)

updater.dispatcher.add_handler(MessageHandler(Filters.text, get_format))
updater.dispatcher.add_handler(CallbackQueryHandler(download_choosen_format))

# Start the Bot
updater.start_polling()
updater.idle()
