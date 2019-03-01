import scipy as sp
import scipy.signal
import matplotlib.pyplot as plt
# import seaborn as sns

f, psd = sp.signal.welch(rawdf[180300:360300], 100, nperseg=1000)
f, psd = sp.signal.periodogram(rawdf[0:10000], 100, nfft=1000)

# Plot the power spectrum
plt.figure(figsize=(11,3))
plt.semilogy(f,psd,'k') # this is the function to make power spectrum fig
sns.despine()
plt.xlim((0,200))
plt.yticks(size=15)
plt.xticks(size=15)
plt.ylabel('power ($uV^{2}/Hz$)',size=15)
plt.xlabel('frequency (Hz)',size=15)
plt.title('PSD of Local Field Potential', size=20)
plt.show()



df = pandas.read_table(filepath)


df1 = df.iloc[30000:90000,1]
df2 = df.iloc[:,1]

a = 1000
ppp, freqenciesFound, time, imageAxis = plt.specgram(output, Fs=100, NFFT = 500, noverlap = 250)

from PIL import Image

w, h = 512, 512
data = np.zeros((h, w, 3), dtype=np.uint8)
data[256, 256] = [255, 0, 0]
img = Image.fromarray(c, 'RGB')
img.save('my.png')
img.show()

a, b, c = spectrogram(df1, )