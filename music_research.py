import librosa
from utility import split_song_collect, collect_map, create_hash, get_scores, get_scores2, fix_rate, window_length_seconds, frequency_bits, split_mp3_time
import os
import pickle

if __name__ == "__main__":
    # 加载数据库
    database = pickle.load(open("./warehouse/database.pickle", 'rb'))
    dic_idx2song = pickle.load(open("./warehouse/song_index.pickle", 'rb'))

    # 要检索的音乐
    file_record = "test/worth it.mp3"
    # 将音频分割成小段去检索
    split_mp3_time(file_record)
    # 获取分割的音频
    song_chunks = split_song_collect()
    # 每段音频对应的匹配值
    chunks_scores = {}

    for song_id, song_name in song_chunks.items():

        # 读取歌曲
        y, fs = librosa.load(song_name, sr=fix_rate)

        # # 规则：仅匹配值
        # scores = get_scores2(y, fs, database)
        #
        # for k, v in scores:
        #     file = dic_idx2song[k]
        #     name = os.path.split(file)[-1]
        #     print(f'{name} : match值为 {v}')

        # 规则：匹配值 + 固定间隔
        # 检索打分
        scores = get_scores(y, fs, database)

        # 打印检索信息
        for k, v in scores:
            # file为歌曲的路径
            file = dic_idx2song[k]
            # name为从file的路径中提取的歌曲名
            name = os.path.split(file)[-1]
            print(f'{name} :  {v[0]} : {v[1]}')
        print("---------------")

    # 打印结果
    # print("检索最终结果为", os.path.split(dic_idx2song[scores[0][0]])[-1])
