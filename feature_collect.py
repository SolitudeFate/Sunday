import librosa
from utility import collect_map, create_hash, song_collect, fix_rate, window_length_seconds, frequency_bits, dividing_line
import os
import pickle

if __name__ == "__main__":

    print(dividing_line)

    # 获取数据库中所有的音乐
    path_music = 'data'
    # 获取绝对路径
    current_path = os.path.abspath(os.path.dirname(__file__))
    path_songs = os.path.join(current_path, path_music)
    dic_idx2song = song_collect(path_songs)

    # 对每条音乐进行特征提取
    database = {}
    # 以列表返回字典所有的键，然后遍历
    for song_id in dic_idx2song.keys():
        file = dic_idx2song[song_id]
        print("正在提取特征 ", file)

        # 读取音乐
        y, fs = librosa.load(file, sr=fix_rate)

        # 提取特征对
        constellation_map = collect_map(y, fs, window_length_seconds=window_length_seconds)

        # 获取hash值
        hashes = create_hash(constellation_map, fs, frequency_bits=frequency_bits, song_id=song_id)

        # 把hash信息填充如数据库
        # time_index_pair是(time, song_id)
        for hash, time_index_pair in hashes.items():
            if hash not in database:
                # 每一个hash键的值为一个列表
                database[hash] = []
            database[hash].append(time_index_pair)

    print(dividing_line)
    print("提取完成")

    # 对数据进行保存
    target_folder = "warehouse"
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    with open("./warehouse/database.pickle", 'wb') as db:
        pickle.dump(database, db, pickle.HIGHEST_PROTOCOL)
    with open("./warehouse/song_index.pickle", 'wb') as songs:
        pickle.dump(dic_idx2song, songs, pickle.HIGHEST_PROTOCOL)

    print(dividing_line)