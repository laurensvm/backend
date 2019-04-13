import os
import eyed3
import youtube_dl

songs_filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "static/songs")


# Get from somewhere
arr = ["https://soundcloud.com/houzmusicblog/premiere-olivier-verhaeghe-rock-with-u"]
# plist = ['https://www.youtube.com/watch?v=oDGjqR9D4oA']


def download_songs(song_list):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'outtmpl': os.path.join(songs_filepath, '%(title)s.%(ext)s'),
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(song_list)


# def clean_song_name(song_filepath):
#     pass

# def update_songs_metadata(songs_filepath):
#     for filename in os.listdir(songs_filepath):
#         if filename[-4:] == ".mp3" and " - " in filename:
#             artist, title = filename[:-4].split(" - ")

#             song = eyed3.load(os.path.join(songs_filepath, filename))
#             song.tag.title = title
#             song.tag.artist = artist
#             song.tag.save()


# update_songs_metadata(songs_filepath)
# download_songs(arr)
