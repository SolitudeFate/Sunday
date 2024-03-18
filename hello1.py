from pydub import AudioSegment
from pydub.utils import make_chunks

# 加载音频文件
audio = AudioSegment.from_file("./test/worth it.mp3", "mp3")

# 切割的毫秒数 1s=1000ms
size = 10000

# 将音频切割为10s一个
chunks = make_chunks(audio, size)

for i, chunk in enumerate(chunks):
    chunk_path = f"test_chunks/song_{i + 1}_part.mp3"
    # 保存每个音频片段
    chunk.export(chunk_path, format="mp3")

