import yt_dlp
import os
import random
def monitor(d):
    filenames.append(d.get('info_dict').get('_filename'))
def rm_r(path):
    for file in os.listdir(working_path):
        os.remove(f'{working_path}\\{file}')
    os.rmdir(working_path)
url = "https://music.youtube.com/playlist?list=OLAK5uy_mO-B6-lxdrHnNLB3vPPLRQVdzDbAZgHxc"
dlp_options = {
        'format': 'bestvideo*+bestaudio/best',
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': False,
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
    rm_r(working_path)

# Create working directory
os.mkdir(working_path)
print("Working path created")
os.chdir(working_path)

# Download playlist
yt_dlp.YoutubeDL(dlp_options).download(url)

# Briefly convert to dict to remove duplicates because of some weird yt_dlp shit
filenames = list(dict.fromkeys(filenames))

# Rename all the files because ffmpeg pissy otherwise
for i, file in enumerate(filenames):
    print(filenames)
    os.rename(file, f'{i}.webm')
    filenames[i] = f'{i}.webm'

random.shuffle(filenames)

# Write list of files for ffmpeg
with open("super_cool_list.txt", 'w') as list:
    for file in filenames:
        list.write(f"file '{file}'\n")

os.system("ffmpeg -safe 0 -f concat -i super_cool_list.txt -c copy ..\Playlist.webm") 

rm_r(working_path)