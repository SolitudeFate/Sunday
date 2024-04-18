import os

import librosa
import numpy as np
from scipy import signal

# 采样率
fix_rate = 8000
# 窗口宽度
window_length_seconds = 0.5
# 10bit量化
frequency_bits = 10

# 分割线
dividing_line = "---------------------------------------"


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


# 进行hash编码（仅时域限制）
def create_hash(constellation_map, fs, frequency_bits=10, song_id=None):
    # 根据奈奎斯特采样准测，频率上限为采样率的一半
    upper_frequency = fs / 2
    hashes = {}
    # 遍历寻找点对
    # 第一层for循环为当前点
    for idx, (time, freq) in enumerate(constellation_map):
        # 第二层for循环，从邻近的200个点中寻找点对
        for other_time, other_freq in constellation_map[idx: idx + 200]:
            diff = other_time - time
            # 对时域进行限制，在200个点中，保留时域相差2到10范围内的点构成点对
            if diff <= 1 or diff > 10:
                continue

            '''
            编码过程：
                将f1和f2进行10bit量化，其余bit用来存储时间偏移，合起来形成32bit的hash嘛
                Hash = bin_f1 | bin_f2 << 10 | diff_t << 20
                Hash:   time = [f1:f2:德尔塔t] : t1
                存储信息为(t1, Hash)

            1、先对freq和other_freq进行二进制编码。
            freq = n/n_fft*fs，根据奈奎斯特采样准测，freq必定小于采样率fs的一半，即小于upper，
            除以upper后为一个0到1之间的值，再乘10bit量化，即乘2的10次，然后取整int()

            2、再对二进制编码后的频率进行10bit量化，编成32位的码。
            '''
            freq_binned = freq / upper_frequency * (2 ** frequency_bits)
            other_freq_binned = other_freq / upper_frequency * (2 ** frequency_bits)

            hash = int(freq_binned) | (int(other_freq_binned) << 10) | (int(diff) << 20)
            # time为点对的起始时间t1
            hashes[hash] = (time, song_id)
    return hashes


'''
检索过程
参数：
     y -> 要检索的音频信号
    fs -> 要检索的音频信号的采样率
'''


# 不仅进行hash码匹配，同时保证时间差固定。先找到匹配的hash，再从匹配到的hash中再进行固定时间差进行筛选
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

    # 对score进行从大到小的排序，也就是对x[1][1]，返回值为排序后的列表，x[1]为value，x[1][1]为score
    scores = sorted(scores.items(), key=lambda x: x[1][1], reverse=True)

    return scores
