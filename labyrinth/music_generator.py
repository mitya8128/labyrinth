
from pyo import*
from tkinter import*

def generate_melody():

    s = Server().boot()
    s.start()
    mod = Sine(freq=50, mul=50)
    mod2 = Sine(freq=100, mul=50)

    t = CosTable([(0, 0), (100, 1), (500, .3), (8191, 0)])
    beat = Beat(time=.125, taps=16, w1=[90, 80], w2=50, w3=35, poly=1).play()  # try taps=10 and larger poly
    trmid = TrigXnoiseMidi(beat, dist=12, mrange=(60, 96))
    trhz = Snap(trmid, choice=[0, 2, 3, 5, 7, 8, 10], scale=1)
    tr2 = TrigEnv(beat, table=t, dur=beat['dur'], mul=beat['amp'])

    mod = Sine(freq=50, mul=50)
    mod2 = Sine(freq=100, mul=50)

    a = Sine(freq=trhz + mod2, mul=tr2 * 0.2).out()
    s.gui(locals())




""""# script #1
a = Sine(freq=mod+mod2+4,mul=0.5).out()

soundfile = SndTable(SNDS_PATH + "/transparent.aif")

src = Looper(soundfile, dur=2, xfade=0, mul=0.3)
src2 = src.mix(2).out()

comb1 = Delay(src, delay=[0.0297, 0.0277], feedback=0.65)
comb2 = Delay(src, delay=[0.0371, 0.0393], feedback=0.51)
comb3 = Delay(src, delay=[0.0411, 0.0409], feedback=0.5)
comb4 = Delay(src, delay=[0.0137, 0.0155], feedback=0.73)

# script#2
# idea from http://ajaxsoundstudio.com/pyodoc/api/classes/triggers.html?highlight=beat#pyo.Beat
# when approaching to high levels of labyrinth script may be changed to Sine(freq=trhz+mod2+mod

t = CosTable([(0,0), (100,1), (500,.3), (8191,0)])
beat = Beat(time=.125, taps=16, w1=[90,80], w2=50, w3=35, poly=1).play()    # try taps=10 and larger poly
trmid = TrigXnoiseMidi(beat, dist=12, mrange=(60, 96))
trhz = Snap(trmid, choice=[0,2,3,5,7,8,10], scale=1)
tr2 = TrigEnv(beat, table=t, dur=beat['dur'], mul=beat['amp'])

mod = Sine(freq=50,mul=50)
mod2 = Sine(freq=100,mul=50)

a = Sine(freq=trhz+mod2, mul=tr2*0.2).out()    # first try without modulations

# 1
# a = Sine(4400000, 2, 0.5).out()

# 2
# mod = Sine(freq=50,mul=50)
# a = Sine(freq=mod+44000,mul=1).out()

# 3
# a = Sine(freq=mod+mod2+44000,mul=0.5).out()
"""""""""""""""'"""'