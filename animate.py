# (C) 2013 by Rupert Lloyd  <rupert.lloyd@gmail.com>
import os
from vizlte import *
import pylab

def frames_in_file(path,samplerate):
    bytes_per_frame = int(2*samplerate*lte_framelen)
    return os.path.getsize(path)/bytes_per_frame

# use the following command line
# ffmpeg -r 10 -i frame_%06d.jpg -s 1080x720 movie.mp4
    

if __name__ == "__main__":
    from optparse import OptionParser
    usage=  """usage: %prog [options...] <file>
Options:
    -r/--rate <freq in Hz>  : sample rate of baseband (samples/s)
    -z/--zoom <freq in Hz>  : center zoom on frequency axis
    -n/--frames <n>         : display <n> radio frames along x-axis
    -i/--interpolation <i>  : image interploation (see http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.imshow)
    -f/--format <format>    : (U8=unsigned 8-bit I/Q, S8=signed 8-bit I/Q)
    -s/--startframe <n>     : start from this frame (default is frame 0)
    -c/--count <n>          : generate <n> frames (default is 100)
"""
    parser = OptionParser(usage)
    parser.add_option("-r", "--rate", dest="samplerate",type='float',default=1.92e6)
    parser.add_option("-f", "--format", dest="sampleformat",default='uint8')
    parser.add_option("-z", "--zoom", dest="zoom",type='float')
    parser.add_option("-n", "--frames", dest="nframes",type='int',default=5)
    parser.add_option("-s", "--startframe", dest="startframe",type='int',default=0)
    parser.add_option("-c", "--count", dest="count",type='int',default=100)
    parser.add_option("-i", "--interpolation", dest="interp",default='none')
    parser.add_option("-o", "--outdir", dest="outdir",default='nonsuch')
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_usage()
        exit(1)

    if options.zoom is None:
        options.zoom = options.samplerate

    try:
        filepath = args[0]
        total_frames = frames_in_file(filepath,options.samplerate)
        assert options.startframe < total_frames, "start frame exceeds total frames in file (%d)" % total_frames
        assert options.startframe + options.count <= total_frames, " end frame exceeds total frames in file (%d)" % total_frames
        assert os.path.exists(filepath), "baseband file %s does not exist" % filepath 
        assert os.path.exists(options.outdir), "out folder %s does not exist" % options.outdir
    except Exception as exc:        
        print '*** Error: %s ***\n' % exc
        parser.print_usage()
        exit(1)

    for i in range(options.startframe,options.startframe + options.count):
        outpath = os.path.join(options.outdir,'frame_%06d.png' % i )
        print 'generating frame %s' % outpath 
        cvals = load_complex_baseband(filepath,
                                options.samplerate,
                                options.nframes,
                                options.sampleformat,
                                nstartframe=i)
        f = spectrogram(cvals,
                        samplerate=options.samplerate,
                        bandzoom=options.zoom,
                        interp=options.interp,
                        nstartframe=i)  
        f.savefig(outpath,bbox_inches='tight', pad_inches=0) 
        pylab.close(f)
