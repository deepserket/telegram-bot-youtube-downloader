# telegram-bot-youtube-downloader

Change TOKEN with your token 

Usage:
  - Send link of video (@vid inline is comfortable)
  - The bot will download the video and send it
      - If the video is larger than 50MB, it is split into smaller parts, 
        which then need to be concatenated (in linux: cat vid.mp4* > vid.mp4)

This script require:
  - Python3 interpreter
  - Telegram python api https://github.com/python-telegram-bot/python-telegram-bot
  - youtube-dl https://github.com/rg3/youtube-dl/ (installed on the machine)

Tips:
  - Use PythonAnyWhere for hosting the bot https://www.pythonanywhere.com



## TODO
  - Improve space-requirement of hard-split (is 2 times size_of_video, the goal is size_of_video + 49MB)
  - Improve soft-split of the videos
  - PEP8
  - Add a queue to manage multiple users
  - Remove duplicates of resolution
