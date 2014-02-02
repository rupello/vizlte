import os
import subprocess

path = os.path.join('samples','live751MHz_bw10MHz_sampled@15.35MHz.S16')
subprocess.call(['python','vizlte.py',path,'--rate','15.36e6','--format','int16','-n','4','-z','11e6','--startframe','2'])
