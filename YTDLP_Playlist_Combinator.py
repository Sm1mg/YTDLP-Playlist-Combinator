import yt_dlp
import os
import random
import sys
import concurrent.futures
from optparse import OptionParser

parser = OptionParser(usage='usage: %prog [options] url')
parser.add_option('-t', '--thread-count', dest='thread_count', type=int, default=8, metavar='THREADS',
                  help="number of threads to download with:  default is 8")
parser.add_option('-f', '--format', dest='format', default='bestvideo*+bestaudio/best',
                  help='format to download using:  default is best audio + best video')
parser.add_option('-o', '--ffmpeg-options', dest='ffmpeg_options', default='-c copy', metavar='OPTIONS',
                  help='''full ffmpeg parameters to use
                  default will try to losslessly append the files (this will error if the inputs are of different resolutions)
                                        ''')
parser.add_option('-p', '--preserve-working-dir', dest='preserve', action="store_true", default=False,
                  help="preserve the working directory between runs, will not delete before or after the script  default is False")
(options, args) = parser.parse_args()
def monitor(d):
    filenames.append(d.get('info_dict').get('_filename'))

def clear_working_path():
    for file in os.listdir(working_path):
        os.remove(f'{working_path}/{file}')
    os.rmdir(working_path)
    print("Working path removed")

def queue_worker(video):
    try:
        yt_dlp.YoutubeDL(dlp_options).download(video)
    except Exception as e:
        print(f'Failed to download {video} because of {e}')
        queue.append(video)
    

if len(args) == 0:
    url = "https://music.youtube.com/playlist?list=OLAK5uy_nmDUsWOMoEcz0SsVqUwir0oxu-k1oUyXE"
else:
    url = args[0]
dlp_options = {
        'format': options.format,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        'extract_flat' : True,
        'lazy_playlist': True,
        'progress_hooks': [monitor]
    }
working_path = os.path.join(os.getcwd(),"working")
filenames = []

# If the working path exists aleady, clear it
if os.path.exists(working_path):
    if not options.preserve:
        clear_working_path()     
else:
# Create working directory
    os.mkdir(working_path)
    print("Working path created")
os.chdir(working_path)

# Gather data on playlist
playlist = yt_dlp.YoutubeDL(dlp_options).extract_info(url, download=False)

# List to store the queue
queue = []

# Fill queue for thread workers
for video in playlist.get('entries'):
    queue.append(video.get('url'))

# Create ThreadPoolExecutor to consume the queue
with concurrent.futures.ThreadPoolExecutor(max_workers=options.thread_count) as executor:
    executor.map(queue_worker, queue)

# Briefly convert to dict to remove duplicates because of some weird yt_dlp quirk
filenames = list(dict.fromkeys(filenames))

# Make sure we've gotten all of the right files
if len(failed := [x for x in filenames if x not in os.listdir(working_path)]) != 0:
    print("Something went wrong while downloading the videos, try turning down thread-count?")
    print(f'The following failed:\n{failed}')
    exit(1)

random.shuffle(filenames)

# Write list of files for ffmpeg
with open("super_cool_list.txt", 'w') as list:
    for file in filenames:
        # Fix 's
        file = file.replace("'", "'\\''")
        list.write(f"file '{file}'\n")

                               #-hide_banner -safe 0 -f concat -i super_cool_list.txt -c:a copy -c:v libsvtav1 -r 1 -g 120 -crf 23 -preset 7 -svtav1-params fast-decode=3
returncode = os.system(f'ffmpeg -hide_banner -safe 0 -f concat -i super_cool_list.txt {options.ffmpeg_options} "..\{playlist.get("title")}.webm"') 
# If files couldn't be losslessly combined
if returncode != 0:
    print("Something went wrong when concatenating the files, giving up.  Have fun!")
    exit(1)

if not options.preserve:
    clear_working_path()

print("Done, have a good day!")
exit(0)