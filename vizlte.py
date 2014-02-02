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


def scale_int2float(dt):
    ' return a function that scales an integer of ype dt to -1. to +1.'
    scale_min = np.iinfo(dt).min
    scale_max = np.iinfo(dt).max
    return lambda x : 2.*float(x - scale_min)/float(scale_max - scale_min)-1.
 
def values2complex(vals,scaler=lambda x:x):
     'convert a linear array of values to complex samples, using scaling function if specified'
     cvals = []
     for i in range(0,len(vals),2):
         cvals.append(complex(scaler(vals[i]),scaler(vals[i+1])))
     return cvals

def load_complex_baseband(path,samplerate,nframes,sampleformat='int8',nstartframe=0.0):
    bytes_per_value = {'float32':4,'int16':2,'uint16':2,'int8':1,'uint8':8}
    'load & convert nframes of 8bit I/Q samples from path'
    values_per_frame = int(2*samplerate*lte_framelen)
    bytes_per_frame = values_per_frame*bytes_per_value[sampleformat]
    # read frame samples
    fd = open(path,'rb')
    fd.seek(bytes_per_frame*nstartframe)
    read_data = numpy.fromfile(file=fd, dtype=dtype(sampleformat),count=values_per_frame*nframes)
    return values2complex(read_data)


def ofdmgrid(cvals,samplerate,subcarrier_spacing):
    """convert time-domain cvals into OFDM frequency/time grid"""
    nfft  = int(samplerate/subcarrier_spacing)
    nsymbolperiods = len(cvals)/nfft
 
    ofdmgrid = numpy.zeros([nsymbolperiods,nfft],dtype=complex)
    for nbin in range(nsymbolperiods):
        binvals = cvals[nfft*nbin:nfft*(nbin+1)]
        fft = (numpy.fft.fftshift(numpy.fft.fft(binvals,nfft)))
        fft[len(fft)/2] = 0. # remove the DC component
        ofdmgrid[nbin] = fft
    return ofdmgrid    


def spectrogram(rxgrid,samplerate,bandzoom=None,interp='none',nstartframe=0):
    """plot a spectrogram of an array of complex samples, cvals, at samplerate samples/s. 
       Plot nframes of data across the x & zoom to the central bandzoom(Hz) in the yaxis
       use interp see http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.imshow""" 

    nfft = len(rxgrid[0])

    fig, ax = subplots(figsize=(16, 9),dpi=80)
    ax.imshow(abs(rxgrid).transpose(),interpolation=interp, aspect='auto',cmap=cm.jet)

    # yticks correspond to resource blocks spacing lte_rb_bw - starting from the center out
    rb_freqs = np.append(-arange(lte_rb_bw,samplerate/2,lte_rb_bw),arange(0.,samplerate/2,lte_rb_bw))
    rb_freqs.sort()
    scaled = [nfft/2.+(nfft*f/samplerate) for f in rb_freqs]
    yticks(scaled,['%2.2f' % (f*1.e-6) for f in rb_freqs])

    # major ticks correspond to frame lengths
    total_ms = 1000.*len(cvals)/samplerate
    timestep = lte_framelen*1000. # 10. ms
    times = arange((nstartframe*lte_framelen*1000.),(nstartframe*lte_framelen*1000.)+total_ms, timestep)

    binvals = arange(0,len(rxgrid),len(rxgrid)/len(times))
    xticks(binvals,times)
    # minor coorespond to sub-framelengths 
    minor_tick_vals = arange(0,len(rxgrid),len(rxgrid)/(10.*len(times)))
    ax.set_xticks(minor_tick_vals, minor=True)

    # limit to signal bandwidth
    if bandzoom is None:
        bandzoom = samplerate
    bandrange = nfft*bandzoom/samplerate    
    ylim([(nfft-bandrange)/2.,(nfft+bandrange)/2.])
    grid(True,color='yellow', linestyle='-', linewidth=0.5, which="minor")
    grid(True,color='white', linestyle='-', linewidth=0.7, which="major")
    return fig

if __name__ == "__main__":
    from optparse import OptionParser
    usage=  """usage: %prog [options...] <file>
Options:
    -r/--rate <freq in Hz>  : sample rate of baseband (samples/s)
    -z/--zoom <freq in Hz>  : center zoom on frequency axis
    -n/--frames <n>         : display <n> radio frames along x-axis
    -i/--interpolation <i>  : image interploation (see http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.imshow)
    -f/--format <format>    : (U8=unsigned 8-bit I/Q, S8=signed 8-bit I/Q)
    -s/--startframe <n>     : start from this frame (default is 0)
"""
    parser = OptionParser(usage)
    parser.add_option("-r", "--rate", dest="samplerate",type='float',default=1.92e6)
    parser.add_option("-f", "--format", dest="sampleformat",default='uint8')
    parser.add_option("-z", "--zoom", dest="zoom",type='float')
    parser.add_option("-n", "--frames", dest="nframes",type='int',default=1)
    parser.add_option("-s", "--startframe", dest="startframe",type='float',default=0.)
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
                                    options.sampleformat,
                                    options.startframe)

    rxgrid = ofdmgrid(cvals,options.samplerate,lte_subcarrier_spacing)

    f = spectrogram(rxgrid,
                options.samplerate,
                bandzoom=options.zoom,
                interp=options.interp,
                nstartframe=options.startframe)
    show()
