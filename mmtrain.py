import miditest
import cPickle
import numpy

# tset = []
# 
# tset.append(miditest.readMidiPitchDur('midi/test-1.midi'))
# tset.append(miditest.readMidiPitchDur('midi/test-2.midi'))
# tset.append(miditest.readMidiPitchDur('midi/test-3.midi'))
# tset.append(miditest.readMidiPitchDur('midi/test-4.midi'))
# tset.append(miditest.readMidiPitchDur('midi/test-5.midi'))
# tset.append(miditest.readMidiPitchDur('midi/test-6.midi'))
# tset.append(miditest.readMidiPitchDur('midi/test-7.midi'))
# tset.append(miditest.readMidiPitchDur('midi/test-8.midi'))
# tset.append(miditest.readMidiPitchDur('midi/test-9.midi'))
# tset.append(miditest.readMidiPitchDur('midi/test-10.midi'))
# tset.append(miditest.readMidiPitchDur('midi/test-11.midi'))
# tset.append(miditest.readMidiPitchDur('midi/test-12.midi'))

# already pkl the miditrainset.pkl as tset

f = open('miditrainset.pkl','rb')
tset = cPickle.load(f)

# compute prior probs and transition probs
prior = []
trans = numpy.zeros(shape=(127,127),dtype=float)

for i in range(127):
        prior.append(0)

for i in range(len(tset)):
        set = tset[i]
        pitchseq = set[0]
        durseq = set[1]
        for j in range(len(pitchseq)):
                pitch = pitchseq[j]
                prior[pitch] += 1
                if j < len(pitchseq)-1:
                        nextpitch = pitchseq[j+1]
                        trans[pitch][nextpitch] += 1
                        
                
prior = numpy.array(prior,dtype=float) / sum(prior)
for i in range(127):
        if sum(trans[i]) != 0:
                trans[i] = trans[i] / sum(trans[i])

with open('mm.pkl','wb') as f:
        cPickle.dump((prior,trans),f)




