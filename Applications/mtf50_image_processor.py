import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline

class ImageProcessor(object):
    def __init__(self, image, show=True):
        self.image = image
        self.show = show

    def ESF(self):
        self.X = self.image[self.image.shape[0]//2,:]
        mu = np.sum(self.X) / self.X.shape[0]  # 計算平均值
        tmp = (self.X[:] - mu) ** 2
        sigma = np.sqrt(np.sum(tmp) / self.X.shape[0])  # 計算標準差
        self.edge_function = (self.X[:] - mu) / sigma  # 計算邊緣強度函數
        self.edge_function = self.edge_function[::3]  # 每3個取樣一次

    def LSF(self):
        self.ESF()  # 計算邊緣強度函數
        self.lsf = self.edge_function[:-2] - self.edge_function[2:]  # 計算線狀線態函數（Line Spread Function）

    def MTF(self):
        self.LSF()  # 計算線狀線態函數
        self.mtf = abs(np.fft.fft(self.lsf))  # 計算幅頻響應（MTF）
        self.mtf = self.mtf[:]/np.max(self.mtf)  # 正規化 MTF
        self.mtf = self.mtf[:len(self.mtf)//2]  # 只保留一半的 MTF 頻譜
        ix = np.arange(self.mtf.shape[0]) / (self.mtf.shape[0])  # 頻率軸
        spline = UnivariateSpline(ix, self.mtf, s=0)  # 使用樣條函數進行光滑處理
        mtf_fit = spline(ix)

        if self.show:
            fig, axs = plt.subplots(1, 2, figsize=(12, 6))
            axs[0].imshow(self.image, cmap='gray')
            axs[0].set_title('灰度图像')
            axs[1].set_title("MTF")
            axs[1].set_xlabel(r'频率 $[cycles/pixel]$')
            axs[1].set_ylabel('MTF')
            p, = axs[1].plot(ix, self.mtf, '-or')
            ll, = axs[1].plot(ix, mtf_fit)
            axs[1].legend([p, ll], ["MTF 值", "樣條適配"])
            axs[1].grid()
            plt.tight_layout()
            plt.show()

        for i in range(1, len(self.mtf)):
            if self.mtf[i-1] >= 0.5 and self.mtf[i] < 0.5:
                freq1, freq2 = ix[i-1], ix[i]
                mtf1, mtf2 = self.mtf[i-1], self.mtf[i]
                mtf50_frequency = freq1 + (0.5 - mtf1) * (freq2 - freq1) / (mtf2 - mtf1)
                return mtf50_frequency
        return None
