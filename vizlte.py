# (C) 2013 by Rupert Lloyd  <rupert.lloyd@gmail.com>
import os
import numpy
from matplotlib.pylab import *

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
def char2float_signed(char):
    val = ord(char)
    if val < 128:
        return float(val)
    else:
        return float(val-256)

# for rtlsdr uses 0-255 maps to -1 to +1
def char2float_usigned(char):
    val = ord(char)
    return (float(val)-127.)/128.0
    
def bytes2complex(buf,sample_format='S8'):
    cvals = []
    if sample_format=='U8':
        char2float = char2float_usigned
    elif sample_format=='S8':
        char2float = char2float_signed
    else:
        raise Exception("don't recognize format %s" % sample_format)

    for i in range(0,len(buf),2):
        cvals.append(complex(char2float(buf[i]),char2float(buf[i+1])))
    return cvals

def ms_values(nsamples,samplerate):
    'return an array of milliseconds for nsamples@samplerate'
    return [x*1000./samplerate for x in range(nsamples)]

def load_complex_baseband(path,samplerate,nframes,sampleformat='S8'):
    'load & convert nframes of 8bit I/Q samples from path'
    bytes_per_frame = int(2*samplerate*lte_framelen)
    # read frame samples
    fd = open(path,'rb')
    framebytes = fd.read(bytes_per_frame*nframes)
    fd.close()
    return bytes2complex(framebytes,sampleformat)

def spectrogram(cvals,samplerate,nframes=1,bandzoom=None,interp='none'):
    """plot a spectrogram of an array of complex samples, cvals, at samplerate samples/s. 
       Plot nframes of data across the x & zoom to the central bandzoom(Hz) in the yaxis
       use interp see http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.imshow""" 

    nfft  = int(samplerate/lte_subcarrier_spacing)
    nbins = len(cvals)/nfft 

    stacked = []
    for nbin in range(nbins):
        binvals = cvals[nfft*nbin:nfft*(nbin+1)]
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
    if bandzoom is None:
        bandzoom = samplerate
    bandrange = nfft*bandzoom/samplerate    
    ylim([(nfft-bandrange)/2.,(nfft+bandrange)/2.])

    grid(color='yellow', linestyle='-', linewidth=0.5)

    show()

if __name__ == "__main__":
    from optparse import OptionParser
    usage=  """usage: %prog [options...] <file>
Options:
    -r/--rate <freq in Hz>  : sample rate of baseband (samples/s)
    -z/--zoom <freq in Hz>  : center zoom on frequency axis
    -n/--frames <n>         : display <n> radio frames along x-axis
    -i/--interpolation <i>  : image interploation (see http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.imshow)
    -f/--format <format>    : (U8=unsigned 8-bit I/Q, S8=signed 8-bit I/Q)
"""
    parser = OptionParser(usage)
    parser.add_option("-r", "--rate", dest="samplerate",type='float',default=30.72e6)
    parser.add_option("-f", "--format", dest="sampleformat",default='S8')
    parser.add_option("-z", "--zoom", dest="zoom",type='float')
    parser.add_option("-n", "--frames", dest="nframes",type='int',default=1)
    parser.add_option("-i", "--interpolation", dest="interp",default='hamming')
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_usage()
        exit(1)
    else:
        filepath = args[0]
        if os.path.exists(filepath) is False:
            print 'baseband file %s not found' % filepath
            exit(1)
    if options.zoom is None:
        options.zoom = options.samplerate

    cvals = load_complex_baseband(  filepath,
                                    options.samplerate,
                                    options.nframes,
                                    options.sampleformat)
    spectrogram(cvals,
                options.samplerate,
                nframes=options.nframes,
                bandzoom=options.zoom,
                interp=options.interp)
