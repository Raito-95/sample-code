import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline

class ImageProcessor(object):
    def __init__(self, image, show=True):
        self.image = image
        self.show = show

    def ESF(self):
        self.X = self.image[self.image.shape[0]//2,:]  # Take the middle row of the image
        mu = np.sum(self.X) / self.X.shape[0]  # Calculate the mean
        tmp = (self.X[:] - mu) ** 2
        sigma = np.sqrt(np.sum(tmp) / self.X.shape[0])  # Calculate the standard deviation
        self.edge_function = (self.X[:] - mu) / sigma  # Calculate the edge spread function (ESF)
        self.edge_function = self.edge_function[::3]  # Downsample by taking every third sample

    def LSF(self):
        self.ESF()  # Calculate the edge spread function
        self.lsf = self.edge_function[:-2] - self.edge_function[2:]  # Calculate the line spread function (LSF)

    def MTF(self):
        self.LSF()  # Calculate the line spread function
        self.mtf = abs(np.fft.fft(self.lsf))  # Calculate the modulation transfer function (MTF)
        self.mtf = self.mtf[:]/np.max(self.mtf)  # Normalize the MTF
        self.mtf = self.mtf[:len(self.mtf)//2]  # Keep only half of the MTF spectrum
        ix = np.arange(self.mtf.shape[0]) / (self.mtf.shape[0])  # Frequency axis
        spline = UnivariateSpline(ix, self.mtf, s=0)  # Smooth the MTF using a spline function
        mtf_fit = spline(ix)

        if self.show:
            fig, axs = plt.subplots(1, 2, figsize=(12, 6))
            axs[0].imshow(self.image, cmap='gray')
            axs[0].set_title('Grayscale Image')
            axs[1].set_title("MTF")
            axs[1].set_xlabel(r'Frequency $[cycles/pixel]$')
            axs[1].set_ylabel('MTF')
            p, = axs[1].plot(ix, self.mtf, '-or')
            ll, = axs[1].plot(ix, mtf_fit)
            axs[1].legend([p, ll], ["MTF Values", "Spline Fit"])
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
