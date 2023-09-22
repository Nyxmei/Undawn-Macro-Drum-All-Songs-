import os
import argparse
from mido import MidiFile
import keyboard
import time

drum_key_mapping = {
    36: '1',
    38: '3',
    40: '2',
}

cymbal_keys = ['0', '9', '8', '7']

all_keys = set(drum_key_mapping.values()) | set(cymbal_keys) | {'3'}

play_state = 'idle'

def midi_playable(event):
    return event.type == 'note_on' and event.velocity > 0

def play(midi, speed):
    global play_state
    play_state = 'playing'

    cymbal_note_to_key = {}

    for event in midi.play():
        if play_state != 'playing':
            break
        if midi_playable(event):
            note = event.note
            if note in drum_key_mapping:
                key = drum_key_mapping[note]
            elif note not in cymbal_note_to_key:
                if cymbal_keys:
                    key = cymbal_keys.pop(0)
                else:
                    continue
                cymbal_note_to_key[note] = key
            else:
                key = cymbal_note_to_key[note]

            keyboard.press(key)
            time.sleep(event.time / speed)
            keyboard.release(key)

def control(midi, speed):
    global play_state
    if play_state == 'playing':
        play_state = 'pause'
    elif play_state == 'idle':
        keyboard.call_later(play, args=(midi, speed), delay=1)

if __name__ == '__main__':
    for key in all_keys:
        keyboard.add_hotkey(key, lambda k: keyboard.press(k), args=(key,), suppress=True, trigger_on_release=True)

    parser = argparse.ArgumentParser(description='MIDI file auto player for drums and cymbals')
    parser.add_argument('midi', nargs="?", type=str, help='path to MIDI file')
    parser.add_argument('--speed', type=float, default=1.0, help='adjust playback speed')
    args = parser.parse_args()
    midi_path = args.midi
    if not midi_path:
        midi_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files/drum_cymbal_example.mid')
    midi_file = MidiFile(midi_path)
    
    print("Press 'F5' to play/pause, and press 'Esc' to exit.\n")
    keyboard.add_hotkey('F5', lambda: control(midi_file, args.speed), suppress=True, trigger_on_release=True)
    keyboard.wait('Esc', suppress=True)
