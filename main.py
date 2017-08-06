import os
import logging
from glob import glob

import youtube_dl
from telegram.ext import Updater, MessageHandler, Filters
from vid_utils import check_dimension

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

updater = Updater(token='TOKEN') # put here the bot's token
dispatcher = updater.dispatcher

ydl_opts = {
	'restrictfilenames': True,
}

def download(bot, update):
    for f in glob('*.mp4*') + glob('*.webm*'): # with glob it isn't possible to check multiple extension in one regex
        os.remove(f) # remove old video(s)
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([update.message.text])
        
        for f in glob('*.mp4*') + glob('*.webm*'): # if the video is bigger than 50MB split it
            check_dimension(f)
            break # check first file
        
        for f in glob('*.mp4*') + glob('*.webm*'): # send document(s)
            bot.send_document(chat_id=update.message.chat_id, document=open(f, 'rb'))
    
    except Exception as e:
        bot.sendMessage(chat_id=update.message.chat_id, text='Error: {}'.format(e))
        logger.info(e)

download_handler = MessageHandler(Filters.text, download)
dispatcher.add_handler(download_handler)

updater.start_polling()
updater.idle()
