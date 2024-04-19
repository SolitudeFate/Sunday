# 将音频分割成10s一段
from pydub import AudioSegment
from pydub.utils import make_chunks


def split_mp3_time(song_path):
    # 加载音频文件
    audio = AudioSegment.from_file(song_path, "mp3")

    # 切割的毫秒数 1s=1000ms
    size = 5000

    # 将音频切割为5s一个
    chunks = make_chunks(audio, size)

    for i, chunk in enumerate(chunks):
        if i == 5:
            chunk_path = f"../test_mp3/未知音频5.mp3"
            # 保存音频片段
            chunk.export(chunk_path, format="mp3")


if __name__ == '__main__':
    split_mp3_time("../data_mp3/《光年之外》G.E.M. 邓紫棋.mp3")
