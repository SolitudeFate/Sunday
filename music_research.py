import asyncio
import os
import pickle

import librosa

from song_information import stream_output
from utility import fix_rate, dividing_line, get_scores


def music_research(song_path, self):
    self.main.label.setText("正在识别歌曲名称......")
    # 加载数据库
    database = pickle.load(open("../warehouse/database.pickle", 'rb'))
    dic_idx2song = pickle.load(open("../warehouse/song_index.pickle", 'rb'))

    # 要检索的音乐
    file_record = song_path

    # 读取歌曲
    y, fs = librosa.load(file_record, sr=fix_rate)

    # 检索打分，规则：匹配值 + 固定间隔
    scores = get_scores(y, fs, database)

    # 打印匹配度降序排列
    # print(scores)

    # 打印检索信息
    for k, v in scores:
        # file为歌曲的路径
        file = dic_idx2song[k]
        # name为从file的路径中提取的歌曲名
        name = os.path.split(file)[-1]
        print(f'{name} :  {v[0]} : {v[1]}')
    print(dividing_line)

    # 打印结果
    result = f"检索最终结果为 {os.path.split(dic_idx2song[scores[0][0]])[-1]}"
    print(result)
    print(dividing_line)

    song_name = os.path.split(dic_idx2song[scores[0][0]])[-1].replace('.mp3', '')
    print("song_name为", song_name)
    print(dividing_line)

    self.main.lineEdit.setText(song_name)
    self.main.label.setText("正在检索歌曲信息......")
    asyncio.run(stream_output(song_name, self))
    self.main.label.setText("识别完成 √")

# if __name__ == '__main__':
#     song_path = "test_mp3/《人鱼的眼泪》EXO.mp3"
#     result, song_name = music_research(song_path)
#     print(result)
#     print(song_name)
