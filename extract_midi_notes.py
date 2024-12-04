import re
import os
from tkinter import messagebox, simpledialog

class MidiNoteExtractor:
    def __init__(self):
        self.note_mapping = {
            "C-1": 0, "C#-1": 1, "D-1": 2, "D#-1": 3, "E-1": 4, "F-1": 5, "F#-1": 6, "G-1": 7, "G#-1": 8, "A-1": 9, "A#-1": 10, "B-1": 11,
            "C0": 12, "C#0": 13, "D0": 14, "D#0": 15, "E0": 16, "F0": 17, "F#0": 18, "G0": 19, "G#0": 20, "A0": 21, "A#0": 22, "B0": 23,
            "C1": 24, "C#1": 25, "D1": 26, "D#1": 27, "E1": 28, "F1": 29, "F#1": 30, "G1": 31, "G#1": 32, "A1": 33, "A#1": 34, "B1": 35,
            "C2": 36, "C#2": 37, "D2": 38, "D#2": 39, "E2": 40, "F2": 41, "F#2": 42, "G2": 43, "G#2": 44, "A2": 45, "A#2": 46, "B2": 47,
            "C3": 48, "C#3": 49, "D3": 50, "D#3": 51, "E3": 52, "F3": 53, "F#3": 54, "G3": 55, "G#3": 56, "A3": 57, "A#3": 58, "B3": 59,
            "C4": 60, "C#4": 61, "D4": 62, "D#4": 63, "E4": 64, "F4": 65, "F#4": 66, "G4": 67, "G#4": 68, "A4": 69, "A#4": 70, "B4": 71,
            "C5": 72, "C#5": 73, "D5": 74, "D#5": 75, "E5": 76, "F5": 77, "F#5": 78, "G5": 79, "G#5": 80, "A5": 81, "A#5": 82, "B5": 83,
            "C6": 84, "C#6": 85, "D6": 86, "D#6": 87, "E6": 88, "F6": 89, "F#6": 90, "G6": 91, "G#6": 92, "A6": 93, "A#6": 94, "B6": 95,
            "C7": 96, "C#7": 97, "D7": 98, "D#7": 99, "E7": 100, "F7": 101, "F#7": 102, "G7": 103, "G#7": 104, "A7": 105, "A#7": 106, "B7": 107,
            "C8": 108, "C#8": 109, "D8": 110, "D#8": 111, "E8": 112, "F8": 113, "F#8": 114, "G8": 115, "G#8": 116, "A8": 117, "A#8": 118, "B8": 119,
            "C9": 120, "C#9": 121, "D9": 122, "D#9": 123, "E9": 124, "F9": 125, "F#9": 126, "G9": 127
        }
        self.midi_to_note = {v: k for k, v in self.note_mapping.items()}

    def extract_note_from_filename(self, filename):
        """Extract MIDI number and note name, validate correctness."""
        # First try to match the exact pattern: number_note
        midi_match = re.match(r'^(\d+)_([A-G]#?\d+)', filename)
        if midi_match:
            midi_num = int(midi_match.group(1))
            note_name = midi_match.group(2)
            # Validate MIDI number matches the note name
            if midi_num in self.midi_to_note and self.midi_to_note[midi_num].replace('-', '') == note_name:
                return midi_num, note_name

        # If no valid MIDI match, try to find any note pattern
        note_pattern = re.search(r'[_-]([A-G]#?\d+)[_-]', filename)
        if note_pattern:
            note_name = note_pattern.group(1)
            if note_name in self.note_mapping:
                midi_num = self.note_mapping[note_name]
                return midi_num, note_name

        return None, None

    def generate_new_filename(self, original_name, midi_num, note_name, instrument_name, group_name):
        """Generate new filename with MIDI number, note name, instrument, and group."""
        extension = os.path.splitext(original_name)[1]
        return f"{midi_num}_{note_name}_{instrument_name}_{group_name}_RR1{extension}"

    def process_filename(self, filename):
        """Process filename and validate correctness."""
        midi_num, note_name = self.extract_note_from_filename(filename)

        if midi_num is None or note_name is None:
            midi_num, note_name = 60, "C4"  # Default to C4 if not found

        instrument_name = "Bass"  # Replace with user input logic
        group_name = "Gadulka_Buzz"  # Replace with user input logic

        return self.generate_new_filename(filename, midi_num, note_name, instrument_name, group_name)

# Example usage
if __name__ == "__main__":
    extractor = MidiNoteExtractor()
    test_files = [
        "03_D0.wav", "04_D#0.wav", "05_E0.wav", "06_F0.wav", "07_F#0.wav",
        "08_G0.wav", "09_G#0.wav", "10_A0.wav", "11_A#0.wav", "12_B0.wav"
    ]

    for filename in test_files:
        print(f"{filename} → {extractor.process_filename(filename)}")
