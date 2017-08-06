import re
import os
from glob import glob
from subprocess import Popen, PIPE
from time import strftime, strptime
# many of these imports serve the commented code...

# this is the hard-split version (files need to be concatenated...)
def check_dimension(f):
    """ If f is larger than 50MB it divides it into files up to 45MB """
    if os.path.getsize(f) > 50 * 1024 * 1023:
        os.system("split -b 45MB {0} {1}".format(f, f))
        os.remove(f)


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
