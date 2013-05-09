import os
import numpy
from matplotlib.pylab import *

# settings for time, samplerate etc.


# calculate some basic LTE time intervals
# see http://lteuniversity.com/get_trained/expert_opinion1/b/hoomanrazani/archive/2009/03/26/the-basic-unit-of-time-in-lte.aspx
lte_ts           = 1./(15000.*2048.)  # base LTE time unit
lte_framelen     = 307200.*lte_ts         # LTE frame length = 10ms
lte_tslotlen     = 15360.*lte_ts          # = 0.5 ms
lte_cp_short     = 144. * lte_ts
lte_cp_short0    = 160. * lte_ts          # the cp for the first symbol is slightly longer
lte_cp_long      = 512. * lte_ts
lte_symlen       = 1./15000.
lte_subframelen  = 2.*lte_tslotlen
lte_subcarrier_spacing = 15000.
lte_rb_bw        = lte_subcarrier_spacing*12.

# note that openlte uses signed bytes
def char2float(char):
    val = ord(char)
    if val < 128:
        return float(val)
    else:
        return float(val-256)
    
def bytes2complex(buf):
    cvals = []
    for i in range(0,len(buf),2):
        cvals.append(complex(char2float(buf[i]),char2float(buf[i+1])))
    return cvals

def ms_values(nsamples,samplerate):
    return [x*1000./samplerate for x in range(nsamples)]



def spectrogram(cvals,samplerate,nframes,interp='none'):
    binlen = lte_symlen/2.
    nbins = nframes*int(lte_framelen/binlen)
    nfft  = int(samplerate/lte_subcarrier_spacing)

    stacked = []
    for nbin in range(nbins):
        binvals = cvals[int(samplerate*binlen)*nbin:int(samplerate*binlen)*(nbin+1)]
        fft = abs(numpy.fft.fftshift(numpy.fft.fft(binvals,nfft)))
        stacked.append(fft)

    fig, ax = subplots(figsize=(24, 12))
    ax.imshow(numpy.vstack(stacked).transpose(),interpolation=interp, aspect='auto',cmap=cm.jet)

    # yticks correspond to resource blocks spacing lte_rb_bw - starting from the center out
    rb_freqs = np.append(-arange(lte_rb_bw,samplerate/2,lte_rb_bw),arange(0.,samplerate/2,lte_rb_bw))
    rb_freqs.sort()
    scaled = [nfft/2.+(nfft*f/samplerate) for f in rb_freqs]
    yticks(scaled,['%2.2f' % (f*1.e-6) for f in rb_freqs])

    # xticks coorespond to timeslots
    timestep = lte_subframelen*1000. # 0.5 ms
    times = arange(0.,nframes*lte_framelen*1000., timestep)
    binvals = arange(0,nbins,nbins/len(times))
    xticks(binvals,times)

    # limit to signal bandwidth
    ylim([700,1350])
    #xlim([0,50])

    grid(color='yellow', linestyle='-', linewidth=0.5)

    show()

if __name__ == "__main__":
    samplerate = 30.72e6 
    path = r'C:\Users\rlloyd\Dropbox\vmshared\baseband\openlte_default.bin'
    nframes = 4
    interp='bilinear'

    assert os.path.exists(path)
    # read samples
    bytes_per_frame = int(2*samplerate*lte_framelen)
    bytes_per_symbol = int(2*samplerate*lte_symlen)
    # read frame samples
    fd = open(path,'rb')
    framebytes = fd.read(bytes_per_frame*nframes)
    fd.close()
    cvals  = bytes2complex(framebytes)
    spectrogram(cvals,samplerate,nframes,interp)
