# Visualize LTE baseband traces

![output example](http://i.imgur.com/cQgw1ik.png "output example")

### Usage Examples

#### Plot 4 frames from a 1.92MHz baseband file captured with [RLT-SDR](http://sdr.osmocom.org/trac/wiki/rtl-sdr)
 ```python
 python vizlte.py samples\live571Mhz_bw10Mhz_sampled@1.92Mhz.U8 --rate 1.92e6 --format uint8 -n 4
 ```

#### Plot 4 frames from a 30.72MHz baseband  file generated by [OpenLTE](http://sourceforge.net/projects/openlte/)
 ```python
 python vizlte.py samples\synth_bw10Mhz_sampled@30.72MHz.S8 --rate 30.72e6 --format int8 -n 4 -z 3e6
 ```

#### Plot 4 frames from a full 10MHz LTE live downlink captured with [bladeRF](http://www.nuand.com/)
    python vizlte.py samples/live751MHz_bw10MHz_sampled@15.35MHz.S16 --rate=15.6e6 --format=int16 -n 4 -z 11e6 -s 2



#### [A playlist](http://www.youtube.com/playlist?list=PLH4IHWtavDd8AcxVIxE9u-CYbFd7qik_6) of movies made with animate.py
