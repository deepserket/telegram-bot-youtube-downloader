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

        cmd = "youtube-dl -F {}".format(self.link)
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).communicate()
        it = iter(str(p[0], 'utf-8').split('\n')) # iterator of output lines

        try:
            while "code  extension" not in next(it): pass # Remove garbage lines
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
                formats.append([format_code, extension, resolution])
        return formats

    def generate_keyboard(self):
        """ Generate a list of InlineKeyboardButton of resolutions """
        kb = []

        for code, extension, resolution in self.formats:
            kb.append([InlineKeyboardButton("{0}, {1}".format(extension, resolution),
                                     callback_data="{} {}".format(code, self.link))]) # maybe callback_data can support a list or tuple?
        return kb

    def download(self, resolution_code):
        cmd = "youtube-dl -f {0} {1}".format(resolution_code, self.link)
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).communicate()

        for line in str(p[0], 'utf-8').split('\n'):
            if "[download] Destination:" in line:
                self.file_name = line[24:] # name of the file

    def check_dimension(self):
        if os.path.getsize(self.file_name) > 50 * 1024 * 1023:
            os.system('split -b 49M "{0}" "{1}"'.format(self.file_name, self.file_name))
            os.remove(self.file_name)
        return glob(escape(self.file_name) + '*')

    @contextmanager
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
