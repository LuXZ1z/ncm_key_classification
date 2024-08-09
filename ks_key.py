import librosa
import numpy as np
import scipy.linalg
from scipy.stats import zscore

from dataclasses import dataclass
from typing import List

Major_list = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
Minor_list = ['Cm', 'C#m', 'Dm', 'D#m', 'Em', 'Fm', 'F#m', 'Gm', 'G#m', 'Am', 'A#m', 'Bm']

Key_list = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'Cm', 'C#m', 'Dm', 'D#m', 'Em', 'Fm', 'F#m', 'Gm', 'G#m', 'Am', 'A#m', 'Bm']
@dataclass
class KeyEstimator:

    # adapted from:
    # https://gist.github.com/bmcfee/1f66825cef2eb34c839b42dddbad49fd

    major = np.asarray(
        [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
    )
    minor = np.asarray(
        [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
    )

    def __post_init__(self):
        self.major = zscore(self.major)
        self.major_norm = scipy.linalg.norm(self.major)
        self.major = scipy.linalg.circulant(self.major)

        self.minor = zscore(self.minor)
        self.minor_norm = scipy.linalg.norm(self.minor)
        self.minor = scipy.linalg.circulant(self.minor)

    def __call__(self, x: np.array) -> List[np.array]:

        x = zscore(x)
        x_norm = scipy.linalg.norm(x)

        coeffs_major = self.major.T.dot(x) / self.major_norm / x_norm
        coeffs_minor = self.minor.T.dot(x) / self.minor_norm / x_norm

        return coeffs_major, coeffs_minor

def estimate_key(audio_file: str, duration: float = None, proportion: float = None, key: str = None):
    try:
        # 加载音频文件，指定加载时长
        if duration is not None:
            y, sr = librosa.load(audio_file, duration=duration)
        elif proportion is not None:
            total_duration = librosa.get_duration(filename=audio_file)
            y, sr = librosa.load(audio_file, duration=total_duration * proportion)
        else:
            y, sr = librosa.load(audio_file)

        # 提取色谱特征
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

        # 计算色谱特征的平均值
        chroma_mean = np.mean(chroma, axis=1)

        # 使用 KeyEstimator 估计调性
        estimator = KeyEstimator()
        coeffs_major, coeffs_minor = estimator(chroma_mean)

        if key == 'major':
            key_coeffs = coeffs_major
            key_list = Major_list
        elif key == 'minor':
            key_coeffs = coeffs_minor
            key_list = Minor_list
        else:
            key_coeffs = np.concatenate((coeffs_major, coeffs_minor))
            key_list = Key_list

        # 找到得分最高的调性
        estimated_key_index = np.argmax(key_coeffs)

        return key_list[estimated_key_index]

    except Exception as e:
        print(f"Error processing {audio_file}: {e}")
        return None
if __name__ == '__main__':

    audio_file = './春奈るな - 君色シグナル.mp3'
    estimate_key(audio_file, key='major')