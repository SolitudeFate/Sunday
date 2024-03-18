from utility import song_collect
import os

# 文件夹
path_music = 'test_chunks'
# 获取绝对路径
current_path = os.path.abspath(os.path.dirname(__file__))
path_songs = os.path.join(current_path, path_music)
test_songs = song_collect(path_songs)

for id, name in test_songs.items():
    print(f"{id}  {name}")
