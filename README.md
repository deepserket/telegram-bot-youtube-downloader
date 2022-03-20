# telegram-bot-youtube-downloader

### This bot is old and not efficient, this repository will be archived.

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
  - Remove duplicates of resolution
  - Add geo-bypass feature
  - Add playlist download feature
    - match title with regex
    - from video x to video y
    - only video uploaded before or after date x
    - max-views or min-views
  - Subtitle download
