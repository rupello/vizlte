import os
import sys
import numpy

if __name__ == "__main__":
    filepath = sys.argv[1]
    assert os.path.exists(filepath)
    with open(filepath,'rb') as fd:
        int16data = numpy.fromfile(fd,'int16')
        float16data = int16data.astype('float32')/2048.
        float16data.tofile(filepath+'.float32')
