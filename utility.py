import numpy as np
import librosa
from scipy import signal
from pydub import AudioSegment
from pydub.utils import make_chunks
import pickle
import os

# 采样率
fix_rate = 8000
# 窗口宽度
window_length_seconds = 0.5
# 10bit量化
frequency_bits = 10


def song_collect(base_path):
    index_songs = 0
    dic_idx2song = {}
    # 读取地址为base_path所有文件
    for roots, dirs, files in os.walk(base_path):
        # 读取存放歌曲的名为data的文件夹
        for file in files:
            # 寻找后缀为MP3的文件
            if file.endswith(".mp3"):
                # 构造歌曲名与歌曲id之间的映射字典，即【id：歌曲名】
                file_song = os.path.join(roots, file)
                dic_idx2song[index_songs] = file_song
                index_songs = index_songs + 1

    return dic_idx2song


def split_song_collect():
    # 音频分割后保存的文件夹
    path_music = 'test_chunks'
    # 获取绝对路径
    current_path = os.path.abspath(os.path.dirname(__file__))
    path_songs = os.path.join(current_path, path_music)
    test_songs = song_collect(path_songs)

    return test_songs

    # for id, name in test_songs.items():
    #     print(f"{id}  {name}")


# 提取局部最大特征点，形成星云图，fs为采样率
def collect_map(y, fs, window_length_seconds=0.5):
    # 将时间为单位的wls换算成采样点单位，fs是1s中有多少点
    win_length = int(window_length_seconds * fs)
    # 步径hop_length为wls的一半，即0.25s
    hop_length = int(win_length // 2)
    # 短时傅里叶变换，傅里叶变换点数n_fft和wl相同
    S = librosa.stft(y, n_fft=win_length, hop_length=hop_length, win_length=win_length)
    # 取出复数矩阵的实部，即频率的振幅
    S = np.abs(S)
    constellation_map = []
    # D为频域的特征维度，T为时域的帧数
    D, T = np.shape(S)
    # print(f"D的值{D}, T的值{T}")
    # 每一帧在频率维度上取15个最大值点
    num_peaks = 15
    # 遍历每一帧
    for i in range(T):
        spectrum = S[:, i]
        '''
        signal.find_peaks()寻找局部最大，distance限制了两个局部最大值之间的最小距离
        peaks是局部最大值的坐标，props是该点的属性
        '''
        peaks, props = signal.find_peaks(spectrum, prominence=0, distance=20)
        n_peaks = min(num_peaks, len(peaks))
        '''
        prominences是局部最大值点的显著性，值越大，显著性越好
        np.argpartition()给显著性从小到大排序，找后面最大的前n_peaks个，返回值为最大值点的编号
        '''
        largest_peaks = np.argpartition(props["prominences"], -n_peaks)[-n_peaks:]

        for peak in peaks[largest_peaks]:
            # 量化是根据真实的频率值进行量化的，所以要计算物理频率值，公式为n/n_fft*fs
            frequency = peak * fs / win_length
            # 保存局部最大点的时频信息
            constellation_map.append([i, frequency])

    return constellation_map


# # 进行hash编码（仅时域限制）
# def create_hash(constellation_map, fs, frequency_bits=10, song_id=None):
#     # 根据奈奎斯特采样准测，频率上限为采样率的一半
#     upper_frequency = fs / 2
#     hashes = {}
#     # 遍历寻找点对
#     # 第一层for循环为当前点
#     for idx, (time, freq) in enumerate(constellation_map):
#         # 第二层for循环，从邻近的200个点中寻找点对
#         for other_time, other_freq in constellation_map[idx: idx + 200]:
#             diff = other_time - time
#             # 对时域进行限制，在200个点中，保留时域相差2到10范围内的点构成点对
#             if diff <= 1 or diff > 10:
#                 continue
#
#             '''
#             编码过程：
#                 将f1和f2进行10bit量化，其余bit用来存储时间偏移，合起来形成32bit的hash嘛
#                 Hash = bin_f1 | bin_f2 << 10 | diff_t << 20
#                 Hash:   time = [f1:f2:德尔塔t] : t1
#                 存储信息为(t1, Hash)
#
#             1、先对freq和other_freq进行二进制编码。
#             freq = n/n_fft*fs，根据奈奎斯特采样准测，freq必定小于采样率fs的一半，即小于upper，
#             除以upper后为一个0到1之间的值，再乘10bit量化，即乘2的10次，然后取整int()
#
#             2、再对二进制编码后的频率进行10bit量化，编成32位的码。
#             '''
#             freq_binned = freq / upper_frequency * (2 ** frequency_bits)
#             other_freq_binned = other_freq / upper_frequency * (2 ** frequency_bits)
#
#             hash = int(freq_binned) | (int(other_freq_binned) << 10) | (int(diff) << 20)
#             # time为点对的起始时间t1
#             hashes[hash] = (time, song_id)
#     return hashes


# 进行hash编码（频域+时域限制）
def create_hash(constellation_map, fs, frequency_bits=10, song_id=None):
    # 根据奈奎斯特采样准测，频率上限为采样率的一半
    upper_frequency = fs / 2
    hashes = {}
    # 遍历寻找点对
    # 第一层for循环为当前点
    for idx, (time, freq) in enumerate(constellation_map):
        # 第二层for循环，从邻近的100个点中寻找点对
        for other_time, other_freq in constellation_map[idx: idx + 200]:
            diff_time = other_time - time
            diff_freq = abs(other_freq - freq)
            # 对时域进行限制，在100个点中，保留时域相差2到10范围内的点构成点对
            if diff_time <= 9 or diff_time > 200 or diff_freq >= 8000:
                continue

            freq_binned = freq / upper_frequency * (2 ** frequency_bits)
            other_freq_binned = other_freq / upper_frequency * (2 ** frequency_bits)

            hash = int(freq_binned) | (int(other_freq_binned) << 10) | (int(diff_time) << 20)
            # time为点对的起始时间t1
            hashes[hash] = (time, song_id)
    return hashes


'''
检索过程
参数：
     y -> 要检索的音频信号
    fs -> 要检索的音频信号的采样率
'''


# 不仅进行hash码匹配，同时保证时间差固定
def get_scores(y, fs, database):
    # 对检索语音提取hash
    constellation = collect_map(y, fs)
    hashes = create_hash(constellation, fs, frequency_bits=10, song_id=None)

    # 获取与数据库中每首歌的hash匹配
    matches_per_song = {}
    # 取出检索语音的一个个hash
    for hash, (sample_time, _) in hashes.items():
        # 如果数据集中存在检索语音的hash
        if hash in database:
            # 取出检索语音hash对应的value
            matching_occurences = database[hash]
            for source_time, song_index in matching_occurences:
                # 如果没有这首歌的统计，则添加上这首歌
                if song_index not in matches_per_song:
                    matches_per_song[song_index] = []
                '''
                注：
                    sample_time是被检测的音频的hash键对应值的起始时间
                    source_time是数据库中匹配到的hash键对应值的起始时间
                '''
                matches_per_song[song_index].append((hash, sample_time, source_time))

    scores = {}
    # 对于匹配的hash，计算测试样本时间和数据库中样本时间的偏差
    for song_index, matches in matches_per_song.items():
        song_scores_by_offset = {}

        # 对相同的偏差进行累计
        for hash, sample_time, source_time in matches:
            # 两个起始点的差
            delta = source_time - sample_time
            if delta not in song_scores_by_offset:
                song_scores_by_offset[delta] = 0
            song_scores_by_offset[delta] += 1

        # 计算每条歌曲的最大累计偏差
        # 第一个0的位置记录时间间隔delta，第二个0的位置记录时间间隔delta发生的次数
        max_score = (0, 0)
        for offset, score in song_scores_by_offset.items():
            if score > max_score[1]:
                max_score = (offset, score)

        scores[song_index] = max_score

    # 对score进行从大到小的排序，也就是对x[1][1]
    scores = sorted(scores.items(), key=lambda x: x[1][1], reverse=True)

    return scores


# 直接进行hash码匹配
def get_scores2(y, fs, database):
    # 对检索语音提取hash
    constellation = collect_map(y, fs)
    hashes = create_hash(constellation, fs, frequency_bits=10, song_id=None)

    # 获取与数据库中每首歌的hash匹配
    matches_per_song = {}
    # 取出检索语音的一个个hash
    for hash, (_, _) in hashes.items():
        # 如果数据集中存在检索语音的hash
        if hash in database:
            # 取出检索语音hash对应的value
            matching_occurences = database[hash]
            for _, song_id in matching_occurences:
                if song_id not in matches_per_song:
                    matches_per_song[song_id] = 0
                matches_per_song[song_id] += 1

    scores = sorted(matches_per_song.items(), key=lambda x: x[1], reverse=True)

    return scores


# 将音频分割成10s一段
def split_mp3_time(file_record):
    # 加载音频文件
    audio = AudioSegment.from_file(file_record, "mp3")

    # 切割的毫秒数 1s=1000ms
    size = 10000

    # 将音频切割为10s一个
    chunks = make_chunks(audio, size)

    for i, chunk in enumerate(chunks):
        chunk_path = f"test_chunks/song_{i + 1}_part.mp3"
        # 保存每个音频片段
        chunk.export(chunk_path, format="mp3")

    print("音频分割完成")


if __name__ == "__main__":
    pass

    # fix_fs = 16000
    # current_path = os.path.abspath (os.path.dirname (__file__))
    # path_songs = os.path.join(current_path,'data')

    # dic_idx2song = song_collect(path_songs)
    # print(dic_idx2song)

    # database = {}
    # for song_id in dic_idx2song.keys():
    #     file = dic_idx2song[song_id]
    #     print("collect info of file ",file)

    #     # 读取音乐
    #     y,fs = librosa.load(file,sr=fix_fs)

    #     # 提取特征对
    #     constellation_map = collect_map(y,fs)

    #     # 获取hash值
    #     hashes = creat_hash(constellation_map,fs,frequency_bits=10,song_id=song_id)

    #     # 把hash信息填充如数据库
    #     for hash, time_index_pair in hashes.items():
    #         if hash not in database:
    #             database[hash] = []
    #         database[hash].append(time_index_pair)

    # # 数据库写入
    # with open("database.pickle", 'wb') as db:
    #     pickle.dump(database, db, pickle.HIGHEST_PROTOCOL)
    # with open("song_index.pickle", 'wb') as songs:
    #     pickle.dump(dic_idx2song, songs, pickle.HIGHEST_PROTOCOL)

    # 检索部分：

    # 加载数据库
    # database = pickle.load(open("database.pickle",'rb'))
    # dic_idx2song = pickle.load(open("song_index.pickle",'rb'))

    # # 读取歌曲
    # file = 'record.m4a'
    # y,fs = librosa.load(file,sr=fix_fs)
    # scores = getscores(y,fs,database)

    # for k,v in scores:
    #     file = dic_idx2song[k]
    #     name = os.path.split(file)[-1]
    #     print('%s :  %d : %d'%(name,v[0],v[1]))

    # print("检索结果为",os.path.split(dic_idx2song[scores[0][0]])[-1])

    # # 提取hash
    # constellation = collect_map(y, fs)
    # hashes = creat_hash(constellation, fs,frequency_bits=10,song_id=None)

    # matches_per_song = {}
    # for hash, (sample_time, _) in hashes.items():
    #     if hash in database:
    #         matching_occurences = database[hash]
    #         for source_time, song_index in matching_occurences:
    #             if song_index not in matches_per_song:
    #                 matches_per_song[song_index] = []
    #             matches_per_song[song_index].append((hash, sample_time, source_time))

    # print(matches_per_song)

    # for key in matches_per_song.keys():
    #     name_song = os.path.split(dic_idx2song[key])[-1]
    #     print("in song %s find %d matched"%(name_song,len(matches_per_song[key])))

    # scores = {}

    # for song_index, matches in matches_per_song.items():
    #     song_scores_by_offset = {}
    #     for hash, sample_time, source_time in matches:
    #         delta = source_time - sample_time
    #         if delta not in song_scores_by_offset:
    #             song_scores_by_offset[delta] = 0
    #         song_scores_by_offset[delta] += 1

    #     max = (0, 0)
    #     for offset, score in song_scores_by_offset.items():
    #         if score > max[1]:
    #             max = (offset, score)

    #     scores[song_index] = max

    # print(scores)

    # file_wav = "十送红军.mp3"
    # y,fs = librosa.load(file_wav,sr=None)

    # window_length_seconds = 0.5
    # win_length =int(window_length_seconds*fs) 
    # hop_length = int(win_length//2)

    # n_fft = 2**(np.ceil(np.log2(win_length)))

    # # frequencies, times, stft = signal.stft(
    # #     y, fs, nperseg=win_length, nfft=win_length, return_onesided=True
    # # )
    # S = librosa.stft(y,n_fft=win_length,hop_length=hop_length,win_length=win_length)

    # S = np.abs(S)
    # constellation_map = []

    # upper_frequency = fs/2
    # frequency_bits =10

    # song_id =1
    # D,T = np.shape(S)
    # num_peaks = 15
    # for i in range(T):
    #     spectrum= S[:,i]
    #     peaks, props = signal.find_peaks(spectrum, prominence=0, distance=200)
    #     n_peaks = min(num_peaks, len(peaks))
    #     largest_peaks = np.argpartition(props["prominences"], -n_peaks)[-n_peaks:]

    #     frequency = i*fs/win_length
    #     # time = i*hop_length/fs
    #     constellation_map.append([i, frequency])
    # database ={}
    # hashes = {}
    # for idx, (time, freq) in enumerate(constellation_map):
    #     for other_time, other_freq in constellation_map[idx : idx + 100]:
    #         diff = other_time - time

    #         if diff <= 1 or diff > 10:
    #             continue

    #         freq_binned = freq / upper_frequency * (2 ** frequency_bits)
    #         other_freq_binned = other_freq / upper_frequency * (2 ** frequency_bits)
    #         hash = int(freq_binned) | (int(other_freq_binned) << 10) | (int(diff) << 20)
    #         hashes[hash] = (time, song_id)

    # for hash, time_index_pair in hashes.items():
    #     if hash not in database:
    #         database[hash] = []
    #     database[hash].append(time_index_pair)
