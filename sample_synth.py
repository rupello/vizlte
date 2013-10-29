import os
import subprocess

path = os.path.join('samples','synth_bw10Mhz_sampled@30.72MHz.S8')
subprocess.call(['python','vizlte.py',path,'--rate','30.72e6','--format','S8','-n','4','-z','3e6'])
