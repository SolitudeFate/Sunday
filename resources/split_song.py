# 生成测试集
# 获取训练集歌曲的随机片段
import random

from pydub import AudioSegment
from pydub.utils import make_chunks

from ui.widget_slots.slots import get_data_songs_path


def split_mp3_time(songs_path):
    for id, song_path in songs_path.items():
        # 加载音频文件
        audio = AudioSegment.from_file(song_path, "mp3")

        # 切割的毫秒数 1s=1000ms
        size = 5000

        # 将音频切割为5s一个
        chunks = make_chunks(audio, size)

        id += 1
        index = random.randint(0, 20)

        for i, chunk in enumerate(chunks):
            if i == index:
                chunk_path = f"../test_mp3/未知音频{id}.mp3"
                # 保存音频片段
                chunk.export(chunk_path, format="mp3")
                print(f"未知音频{id}.mp3已生成")

if __name__ == '__main__':
    songs_path = get_data_songs_path()
    split_mp3_time(songs_path)
