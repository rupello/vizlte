import os
import subprocess

path = os.path.join('samples','live571Mhz_bw10Mhz_sampled@1.92Mhz.U8')
subprocess.call(['python','vizlte.py',path,'--rate','1.92e6','--format','U8','-n','4'])
