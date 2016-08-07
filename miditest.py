import pretty_midi
from scipy.io.wavfile import write
import IPython.display

# Load MIDI file into PrettyMIDI object

infile = 'midi/test-1.midi'

def readMidiPitchDur(infile):
    pitchseq = []
    durseq = []
    midi_data = pretty_midi.PrettyMIDI(infile)
    for instrument in midi_data.instruments:
        # Don't want to shift drum notes
        if not instrument.is_drum:
            for note in instrument.notes:
                pitch = note.pitch
                dur =  note.end - note.start
                pitchseq.append(pitch)
                durseq.append(dur)
    return (pitchseq,durseq)

midi_data = pretty_midi.PrettyMIDI(infile)
audio_data = midi_data.synthesize()
# IPython.display.Audio(data=audio_data,rate=44100)
write('test.wav', 44100, audio_data)