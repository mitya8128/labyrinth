from pyo import *

s = Server().boot()
s.start()

# 1
# a = Sine(4400000, 2, 0.5).out()

# 2
# mod = Sine(freq=50,mul=50)
# a = Sine(freq=mod+44000,mul=1).out()

# 3
# a = Sine(freq=mod+mod2+44000,mul=0.5).out()


mod = Sine(freq=50,mul=50)
mod2 = Sine(freq=100,mul=50)

a = Sine(freq=mod+mod2+4,mul=0.5).out()

soundfile = SndTable(SNDS_PATH + "/transparent.aif")

src = Looper(soundfile, dur=2, xfade=0, mul=0.3)
src2 = src.mix(2).out()

comb1 = Delay(src, delay=[0.0297, 0.0277], feedback=0.65)
comb2 = Delay(src, delay=[0.0371, 0.0393], feedback=0.51)
comb3 = Delay(src, delay=[0.0411, 0.0409], feedback=0.5)
comb4 = Delay(src, delay=[0.0137, 0.0155], feedback=0.73)
