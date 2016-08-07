# this process transforms a chord sequence to a chord-scale sequence



import scipy.io as sio
import cPickle
import numpy
from collections import OrderedDict
import miditest
import pretty_midi
from scipy.io.wavfile import write

infile = 'test-c.lab'
jdictfile = open('jdict.pkl','rb')

jdict = cPickle.load(jdictfile)
# transfer the chordmode-jazz.mat
# jmat = 'chordmode-jazz.mat'
# jdict = OrderedDict()

# mat = sio.loadmat(jmat)
# chordmode = mat['chordmode']
# lenrange = len(chordmode[0])
# for i in range(lenrange):
#         print chordmode[0][i][0]
#         print chordmode[1][i][0]
#         
#         chordtones = chordmode[0][i][0]
#         chordname = chordmode[1][i][0]
#         
#         jdict[chordname] = chordtones
# 
# print jdict

# scan chord sequence in
chordf = open(infile)
chordseq = []
timeseq = []
for line in chordf:
        # print line
        # stripe out the chord sequence
        tokens_ = line.split(' ') # FIXME: might be '\t' here sometimes
        ch_ = tokens_[2]
        # print ch_
        tokens = ch_.split('\n')
        ch = tokens[0]
        # print tokens
        chordseq.append(ch)
        time = tokens_[0]
        endtime = tokens_[1]
        timeseq.append(float(time))
        print time
timeseq.append(float(endtime))
        
# print chordseq

# root to number
def root2num(root):
        if root == 'C' or root == 'B#':
                num = 0
        if root == 'C#' or root == 'Db':
                num = 1
        if root == 'D':
                num = 2
        if root == 'Eb' or root == 'D#':
                num = 3
        if root == 'E' or root == 'Fb':
                num = 4
        if root == 'F' or root == 'E#':
                num = 5
        if root == 'F#' or root == 'Gb':
                num = 6
        if root == 'G':
                num = 7
        if root == 'G#' or root == 'Ab':
                num = 8
        if root == 'A':
                num = 9
        if root == 'A#' or root == 'Bb':
                num = 10
        if root == 'B' or root == 'Cb':
                num = 11
                   
        return num

def pitch2class(p):
        pc = p % 12
        return pc

# scan chordseq to get rootnumseq and qualityseq
# get the chord template sequence
ctseq = []
rootnumseq = []
rootseq = []
for i in range(len(chordseq)):
        ch = chordseq[i]
        print ch
        tokens = ch.split(':')
        root = tokens[0]
        ct = []
        for i in range(12):
                ct.append(0)
                
        if root == 'N':
                ctseq.append(ct)
                num = -1
                rootnumseq.append(num)
                rootseq.append(root)
        else:
                quality = tokens[1]
                num = root2num(root)
                rootseq.append(root)
                rootnumseq.append(num)
                tones = jdict[quality]
                ts = num + tones
                # print ts
        
                for i in range(len(ts)):
                      pcts = pitch2class(ts[i])
                      ct[pcts] = 1
                ct[num] = 1
                ctseq.append(ct)
        print ct
        
# set a context window, and scan through the ctseq using this window
# create a scalesalience sequence out of that
contextwin = 3
ssseq = []
for i in range(len(ctseq)):
        pre = max(i-1,0)
        cur = i
        next = min(i+1,len(ctseq)-1)
        contextct = [ctseq[pre],ctseq[cur],ctseq[next]]
        # print contextct
        scalesalience = numpy.mean(contextct, axis=0)
        ssseq.append(scalesalience)
        
print ssseq

# here define some templates for the scales
scaletempseq = []
Ionian = [1,0,1,0,1,1,0,1,0,1,0,1]
scaletempseq.append(Ionian)
Dorian = [1,0,1,1,0,1,0,1,0,1,1,0]
scaletempseq.append(Dorian)
Phrygian = [1,1,0,1,0,1,0,1,1,0,1,0]
scaletempseq.append(Phrygian)
Lydian = [1,0,1,0,1,0,1,1,0,1,0,1]
scaletempseq.append(Lydian)
Mixolydian = [1,0,1,0,1,1,0,1,0,1,1,0]
scaletempseq.append(Mixolydian)
Aeolian = [1,0,1,1,0,1,0,1,1,0,1,0]
scaletempseq.append(Aeolian)
Locrian = [1,1,0,1,0,1,1,0,1,0,1,0]
scaletempseq.append(Locrian)
HarmonicMin = [1,0,1,1,0,1,0,1,1,0,0,1]
scaletempseq.append(HarmonicMin)
MelodicMin=[1,0,1,1,0,1,0,1,0,1,0,1]
scaletempseq.append(MelodicMin)

# totally 9 scales
def scalechoice(num):
        if num == 0:
                scale = 'Ionian'
        if num == 1:
                scale = 'Dorian'
        if num == 2:
                scale = 'Phrygian'
        if num == 3:
                scale = 'Lydian'
        if num == 4:
                scale = 'Mixolydian'
        if num == 5:
                scale = 'Aeolian'
        if num == 6:
                scale = 'Locrian'
        if num == 7:
                scale = 'HarmonicMin'
        if num == 8:
                scale = 'MelodicMin'
        return scale

# now compute the scale fits for each chord position

scaleseq = []
fitseqseq = []
bestfitseq = []
for i in range (len(ssseq)):
        ch = chordseq[i]
        root = rootseq[i]
        rootnum = rootnumseq[i]
        scalesalience = ssseq[i]
        fitseq = []     
        for j in range(len(scaletempseq)):
                scaletemp = scaletempseq[j]
                # transpose the scale template to the correct root base
                chordscaletemp = numpy.roll(scaletemp,rootnum)
                # while the scalesalience is already in original positin with correct root base
                scalefit = numpy.dot(scalesalience,chordscaletemp)
                fitseq.append(scalefit)
        fitseqseq.append(fitseq)
        bestfit = numpy.argmax(fitseq)
        bestfitseq.append(bestfit)
        scale = scalechoice(bestfit)
        print ch,'::', root,'-',scale
        scaleseq.append(scale)

# laod the markov chain for pitch transitions
f = open('mm.pkl','rb')
(prior,trans) = cPickle.load(f)


# build the pitch sequence based on the chord-scale sequence
pseqseq = []
for i in range(len(scaleseq)):
        rootnum = rootnumseq[i]
        bestfit = bestfitseq[i]
        scaletemp = scaletempseq[bestfit]
        chordscale = numpy.roll(scaletemp,rootnum)
        # print chordscale
        # roll the chord-scale in midi pitches
        midichordscale = []
        for j in range(127):
                midichordscale.append(0)
        # print midichordscale
        for j in range(127):
                midichordscale[j] = chordscale[j%12]
                
        # print midichordscale
        
        pseq = []
        # generate 8 equal length pitches
        # first pick a random note from the prior
        while 1:
                p1 = numpy.random.choice(127,1,p=prior)
                if midichordscale[p1[0]] == 1:
                        break
        
        pseq.append(p1[0])
        
        # for the consequential 7 pitches, choose from trans
        for k in range(7):
                prev = pseq[k]
                while 1:
                        cur_ = numpy.random.choice(127,1,p=trans[prev])
                        cur = cur_[0]
                        if midichordscale[cur] == 1:
                                break
                pseq.append(cur)
        print pseq
        pseqseq.append(pseq)
        
# create midi files from pseq
guitar_c_chord = pretty_midi.PrettyMIDI()
# Create an Instrument instance for a guitar instrument
guitar_program = pretty_midi.instrument_name_to_program('Electric Guitar (jazz)')
guitar = pretty_midi.Instrument(program=guitar_program)
# Iterate over note names, which will be converted to note number later
bartime = 0
print timeseq
for i in range(len(pseqseq)):
        
        # first play the chord
        ct = ctseq[i]
        chordtones = []
        for j in range(12):
                if ct[j] == 1:
                        chordtones.append(j+60)
        print chordtones
        for note_number in chordtones:
            note = pretty_midi.Note(velocity=70, pitch=note_number, start=timeseq[i], end=timeseq[i+1])
            guitar.notes.append(note)
        
        # then play "licks"
        pseq = pseqseq[i]
        swing = 0
        dur = (timeseq[i+1] - timeseq[i])/4
        pretime = timeseq[i]
        for note_number in pseq:
            if swing % 2 == 0:
                note = pretty_midi.Note(velocity=80, pitch=note_number, start=pretime, end=pretime+dur/3)
            else:
                note = pretty_midi.Note(velocity=70, pitch=note_number, start=pretime + 2*dur/3, end=pretime+dur)
                pretime = pretime + dur
            guitar.notes.append(note)
            swing += 1
        
# Add the guitar instrument to the PrettyMIDI object
guitar_c_chord.instruments.append(guitar)
# Write out the MIDI data
guitar_c_chord.write('guitar-chord-melody.mid')
audio_data = guitar_c_chord.synthesize()
# IPython.display.Audio(data=audio_data,rate=44100)
write(infile+'.wav', 44100, audio_data)