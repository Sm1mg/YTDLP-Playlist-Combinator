import yt_dlp
import os
import random
import sys
import threading

thread_count = 8

def monitor(d):
    filenames.append(d.get('info_dict').get('_filename'))
def clear_working_path():
    for file in os.listdir(working_path):
        os.remove(f'{working_path}/{file}')
    os.rmdir(working_path)
    print("Working path removed")

def queue_worker():
    os.chdir(working_path)
    # While the queue isn't empty, consume links and download them
    while queue:
        video = queue.pop()
        yt_dlp.YoutubeDL(dlp_options).download(video)

if len(sys.argv) == 1:
    url = "https://music.youtube.com/playlist?list=OLAK5uy_nmDUsWOMoEcz0SsVqUwir0oxu-k1oUyXE"
else:
    url = sys.argv[1]
dlp_options = {
        'format': 'bestvideo*+bestaudio/best',
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': False,
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
    clear_working_path()     

# Create working directory
os.mkdir(working_path)
print("Working path created")
os.chdir(working_path)

# Gather data on playlist
playlist = yt_dlp.YoutubeDL(dlp_options).extract_info(url, download=False)

# List to store the threads and their queue
threads = []
queue = []

# Fill queue for thread workers
for video in playlist.get('entries'):
    queue.append(video.get('url'))

# Create thread to download each video
for i in range(thread_count):
    url = video.get('url')
    thread = threading.Thread(target=queue_worker)
    threads.append(thread)
    thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()

# Briefly convert to dict to remove duplicates because of some weird yt_dlp shit
filenames = list(dict.fromkeys(filenames))

# Make sure the number of files matches what we're expecting
if len(os.listdir(working_path)) != len(filenames):
    print("Something went wrong while downloading the videos, try turning down thread_count?")

# Rename all the files because ffmpeg pissy otherwise
for i, file in enumerate(filenames):
    os.rename(file, f'{i}.webm')
    filenames[i] = f'{i}.webm'

random.shuffle(filenames)

# Write list of files for ffmpeg
with open("super_cool_list.txt", 'w') as list:
    for file in filenames:
        list.write(f"file '{file}'\n")

returncode = os.system(f'ffmpeg -safe 0 -f concat -i super_cool_list.txt -c copy "..\{playlist.get("title")}.webm"') 
# If files couldn't be losslessly combined
if returncode != 0:
    print("Something went wrong when concatenating the files, giving up.  Have fun!")
    exit()

clear_working_path()

print("Done, have a good day!")