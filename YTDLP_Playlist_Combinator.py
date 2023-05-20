import yt_dlp
import os
import random
import sys
def monitor(d):
    filenames.append(d.get('info_dict').get('_filename'))
def clear_working_path():
    for file in os.listdir(working_path):
        os.remove(f'{working_path}\\{file}')
    os.rmdir(working_path)

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
        'lazy_playlist': True,
        'progress_hooks': [monitor]
    }
working_path = os.path.join(os.getcwd(),"working")
filenames = []

# Clear working path if it exists
if os.path.exists(working_path):
    clear_working_path()

# Create working directory
os.mkdir(working_path)
print("Working path created")
os.chdir(working_path)

# Download playlist
playlist = yt_dlp.YoutubeDL(dlp_options).extract_info(url)

# Briefly convert to dict to remove duplicates because of some weird yt_dlp shit
filenames = list(dict.fromkeys(filenames))

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
# If files couldn't be concat-ed

clear_working_path()

print("Done, have a good day!")