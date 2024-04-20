import os
import re

from utility import song_collect

# 获取data集中所有的音乐
def get_data_songs_path():
    path_music = 'data_mp3'
    current_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    path_songs = os.path.join(current_path, path_music)
    dic_idx2song = song_collect(path_songs)
    return dic_idx2song

# 获取test集中所有的音乐
def get_test_songs_path():
    path_music = 'test_mp3'
    current_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    path_songs = os.path.join(current_path, path_music)
    dic_idx2song = song_collect(path_songs)
    return dic_idx2song


# 读取文件，加载所有下拉选项
def add_all_items(combo_box):
    songs = get_test_songs_path()
    combo_box.addItem('未选择')
    for song_id, song_path in songs.items():
        song_name = os.path.split(song_path)[-1]
        combo_box.addItem(song_name)


# 从test集中寻找该歌曲
def find_test_song(song_name):
    dir_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    dir_name = "test_mp3"
    songs_path = os.path.join(dir_path, dir_name)
    song_path = ''
    for roots, dirs, files in os.walk(songs_path):
        for file in files:
            if file.endswith(".mp3"):
                if re.search(song_name, file):
                    song_path = os.path.join(roots, file)
                    return song_path


# 从data集中寻找该歌曲
def find_data_song(song_name):
    dir_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    dir_name = "data_mp3"
    songs_path = os.path.join(dir_path, dir_name)
    song_path = ''
    for roots, dirs, files in os.walk(songs_path):
        for file in files:
            if file.endswith(".mp3"):
                if re.search(song_name, file):
                    song_path = os.path.join(roots, file)
    return song_path


if __name__ == '__main__':
    song_path = find_data_song("《Bea")
    print(song_path)
