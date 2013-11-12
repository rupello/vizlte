import os
import sys
import numpy

if __name__ == "__main__":
    filepath = sys.argv[1]
    assert os.path.exists(filepath)
    with open(filepath,'rb') as fd:
        int16data = numpy.fromfile(fd,'int16')
        int8data = numpy.right_shift(int16data,4)
        int8data.astype('int8').tofile(filepath+'.int8')
