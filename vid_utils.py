import re
import os
from glob import glob, escape
from subprocess import Popen, PIPE
from time import strftime, strptime, sleep
from contextlib import contextmanager

from telegram import InlineKeyboardButton

class BadLink(Exception):
    pass


class Video:
    def __init__(self, link, init_keyboard=False):
        self.link = link
        self.file_name = None
        
        if init_keyboard:
            self.formats = self.get_formats()
            self.keyboard = self.generate_keyboard()

    def get_formats(self):
        formats = []

        cmd = "youtube-dl -F {}".format(self.link)# this command return the video info to string
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).communicate()
        # creat subprocess,args is a string, the string is interpreted as the name or path of the program to execute
        #If shell is True, it is recommended to pass args as a string rather than as a sequence.
        #communicate() returns a tuple (stdoutdata, stderrdata).
        #communicate() Interact with process: Send data to stdin. Read data from stdout and stderr, until end-of-file is reached. Wait for process to terminate.

        it = iter(str(p[0], 'utf-8').split('\n')) # stdoutdata split with /n in a array to a iterate
        #iter([a,b,c])

        try:
            while "code  extension" not in next(it): pass #if has not this string then goto next line
        except StopIteration:
            raise BadLink # Isn't a valid youtube link

        while True:
            try:
                line = next(it)
                if not line:
                    raise StopIteration # Usually the last line is empty
                if "video only" in line:
                    continue # I don't need video without audio
            except StopIteration:
                break
            else:
                format_code, extension, resolution, *_ = line.strip().split()
                #strip() Remove spaces at the beginning and at the end of the string

                formats.append([format_code, extension, resolution])
        return formats

    def generate_keyboard(self):
        """ Generate a list of InlineKeyboardButton of resolutions """
        kb = []

        for code, extension, resolution in self.formats:
            kb.append([InlineKeyboardButton("{0}, {1}".format(extension, resolution),
                                     callback_data="{0} {1}".format(code, self.link))]) #Data to be sent in a callback query to the bot, will trige CallbackQueryHandler in main.py
        return kb

    def download(self, resolution_code):
        cmd = "youtube-dl -f {0} {1}".format(resolution_code, self.link)# download video command
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).communicate()

        for line in str(p[0], 'utf-8').split('\n'):
            if "[download] Destination:" in line:
                self.file_name = line[24:] # name of the file

    def check_dimension(self):
        if os.path.getsize(self.file_name) > 50 * 1024 * 1023:# big than 50mb
            os.system('split -b 49M {0} {1}'.format(self.file_name, self.file_name))
            #os.system() run real command in your machine

            os.remove(self.file_name)#remove orignal file
        return glob.escape(self.file_name + '*')# return files match in glob.escape('') without special character

    @contextmanager #run this function with new defined send function
    def send(self):
        files = self.check_dimension() # split if size >= 50MB
        yield files
        for f in files: #removing old files
            os.remove(f)





#__________________________OLD STUFFS, TOUCH CAREFULLY__________________________

# this is the soft-split version, require avconv, but the audio isn't synchronized, avconv's problems :(
'''
def get_duration(filepath): # get duration in seconds
    cmd = "avconv -i %s" % filepath
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    di = p.communicate()
    for line in di:
        if line.rfind(b"Duration") > 0:
            duration = str(re.findall(b"Duration: (\d+:\d+:[\d.]+)", line)[0])
    return 3600 * int(duration[2: 4]) + 60 * int(duration[5: 7]) + int(duration[8: 10])

def check_dimension(f): # if f is bigger than 50MB split it in subvideos
    if os.path.getsize(f) > 50 * 1024 * 1023:
        duration = get_duration(f)
        for i in range(0, duration, 180):
            start = strftime("%H:%M:%S", strptime('{0} {1} {2}'.format(i // 3600, (i // 60) % 60, i % 60), "%H %M %S")) # TODO this is  not pythonic code!
            os.system("""avconv -i '{0}' -vcodec copy -acodec copy -ss {1} -t {2} 'part_{3}.mp4'""".format(f, start, 180, (i // 180) % 180))
        os.remove(f) # delete original file
'''
