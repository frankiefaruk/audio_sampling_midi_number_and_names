import tkinter as tk
from tkinter import messagebox, filedialog
import tkinter.ttk as ttk
import os
from extract_midi_notes import MidiNoteExtractor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import re
import shutil

class AudioFileRenamerTextFileGenerator:
    def __init__(self, root):
        # Basic window setup
        self.root = root
        self.root.title("Audio File Renamer / Text File Generator")
        
        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Calculate window size
        window_width = int(screen_width * 0.25)
        window_height = int(screen_height * 0.8)
        
        # Calculate position for center of screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set window size and position
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Define minimum window size
        self.root.minsize(300, 600)
        
        # Define colors and fonts
        self.DARK_GREY = '#333333'
        self.DARKER_GREY = '#444444'
        self.TEXT_COLOR = 'white'
        
        # Define font sizes
        self.HEADER_FONT = ('Segoe UI', 17)
        self.ENTRY_FONT = ('Segoe UI', 17)
        self.BUTTON_FONT = ('Segoe UI', 17)
        self.PREVIEW_FONT = ('Segoe UI', 17)
        self.RADIO_FONT = ('Segoe UI', 17)
        
        # Configure root background
        self.root.configure(bg=self.DARK_GREY)
        
        # Create main container
        main_frame = ttk.Frame(root, style='Main.TFrame', padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Initialize the note extractor
        self.note_extractor = MidiNoteExtractor()
        
        # Create the interface
        self.create_interface(main_frame)

    def create_interface(self, container):
        # Common input fields frame
        input_frame = ttk.Frame(container, style='Panel.TFrame')
        input_frame.pack(fill='x', pady=(0, 10))

        # Name Entry
        ttk.Label(input_frame, text="Enter Name (e.g., Electric_Guitar)", style='Header.TLabel').pack(anchor='w')
        self.name_entry = ttk.Entry(input_frame, style='Dark.TEntry')
        self.name_entry.pack(fill='x', pady=(0,10))
        
        # Note Range Entry
        ttk.Label(input_frame, text="Enter Note Range (e.g., E2-E6)", style='Header.TLabel').pack(anchor='w')
        self.note_range_entry = ttk.Entry(input_frame, style='Dark.TEntry')
        self.note_range_entry.pack(fill='x', pady=(0,10))

        # Preview section
        ttk.Label(container, text="Preview", style='Header.TLabel').pack(anchor='w')
        self.preview_text = tk.Text(container, height=10, bg='#2d2d2d', fg='white')
        self.preview_text.pack(fill='both', expand=True, pady=(0,10))
        self.preview_text.config(state='disabled')

        # Buttons frame
        button_frame = ttk.Frame(container, style='Panel.TFrame')
        button_frame.pack(fill='x', pady=(0,10))

        # Store the submit button as an instance variable
        self.submit_button = ttk.Button(
            button_frame,
            text="Submit",
            style='Control.TButton',
            command=self.on_submit
        )
        self.submit_button.pack(side='left', padx=5)

        ttk.Button(
            button_frame,
            text="Clear",
            style='Control.TButton',
            command=self.clear_all
        ).pack(side='left', padx=5)

        # Bind entry fields for live updates
        self.name_entry.bind('<KeyRelease>', self.on_entry_change)
        self.note_range_entry.bind('<KeyRelease>', self.on_entry_change)

    def on_entry_change(self, event=None):
        """Handle entry field changes - only update preview"""
        self.update_preview()

    def on_submit(self):
        """Handle submit button press"""
        base_name = self.name_entry.get().strip()
        note_range = self.note_range_entry.get().strip()
        
        if base_name and note_range:
            try:
                start_note, end_note = [n.strip() for n in note_range.split('-')]
                start_midi = self.note_extractor.note_mapping.get(start_note)
                end_midi = self.note_extractor.note_mapping.get(end_note)
                
                if start_midi is not None and end_midi is not None and start_midi <= end_midi:
                    self.create_action_dialog()
                else:
                    messagebox.showerror("Error", "Invalid note range format. Example: E2-E6")
            except ValueError:
                messagebox.showerror("Error", "Invalid note range format. Example: E2-E6")
        else:
            messagebox.showerror("Error", "Please fill in both name and note range fields.")

    def update_preview(self):
        """Update preview based on current inputs"""
        if not self.preview_text:
            return

        try:
            preview_text = ""
            base_name = self.name_entry.get().strip()
            note_range = self.note_range_entry.get().strip()

            if base_name:
                if note_range:
                    try:
                        start_note, end_note = [n.strip() for n in note_range.split('-')]
                        # Use note_mapping from MidiNoteExtractor
                        start_midi = self.note_extractor.note_mapping.get(start_note)
                        end_midi = self.note_extractor.note_mapping.get(end_note)
                        
                        if start_midi is None or end_midi is None:
                            preview_text = "Invalid note range format. Example: E2-E6"
                        elif start_midi > end_midi:
                            preview_text = "Start note must be lower than end note"
                        else:
                            for midi_num in range(start_midi, end_midi + 1):
                                note_name = self.note_extractor.midi_to_note[midi_num]
                                new_name_with_extension = f"{midi_num}_{note_name}_{base_name}.wav"
                                new_name_without_extension = os.path.splitext(new_name_with_extension)[0]
                                preview_text += f"{new_name_without_extension}\n"
                    except ValueError:
                        preview_text = "Invalid note range format. Example: E2-E6"
                else:
                    preview_text = "Enter note range to see preview..."
            else:
                preview_text = "Enter a name to see preview..."

            # Update preview text
            self.preview_text.config(state='normal')
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, preview_text)
            self.preview_text.config(state='disabled')

        except Exception as e:
            print(f"Preview update error: {str(e)}")

    def create_text_file(self):
        """Create text file with file names"""
        base_name = self.name_entry.get().strip()
        if not base_name:
            messagebox.showwarning("Warning", "Please enter a name first.")
            return False

        try:
            # Get note range
            note_range = self.note_range_entry.get().strip()
            if note_range:
                # Parse user-defined range
                start_note, end_note = [n.strip() for n in note_range.split('-')]
                start_midi = self.note_extractor.note_mapping.get(start_note)
                end_midi = self.note_extractor.note_mapping.get(end_note)
                
                if start_midi is None or end_midi is None:
                    messagebox.showerror("Error", "Invalid note range format. Example: C#3-B5")
                    return False
            else:
                # Use full MIDI range
                start_midi = 0  # C-1
                end_midi = 127  # G9

            # Create file content
            file_content = ""
            for midi_num in range(start_midi, end_midi + 1):
                note_name = self.note_extractor.midi_to_note[midi_num]
                filename = f"{midi_num}_{note_name}_{base_name}.wav\n"
                file_content += filename

            # Save file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")],
                initialfile=f"{base_name}_names.txt"
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(file_content)
                messagebox.showinfo("Success", "Text file has been created.")
                return True

        except Exception as e:
            messagebox.showerror("Error", f"Error creating text file: {str(e)}")
            return False

        return False

    def clear_all(self):
        """Clear all entries and reset the form"""
        # Clear all entry fields
        self.name_entry.delete(0, tk.END)
        self.note_range_entry.delete(0, tk.END)
        
        # Reset preview
        self.preview_text.config(state='normal')
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, "Preview will appear here...")
        self.preview_text.config(state='disabled')
        
        # Show confirmation message
        messagebox.showinfo("Clear", "All fields have been cleared!")

    def __del__(self):
        """Clean up observer when the application closes"""
        self.stop_folder_watch()

    def create_action_dialog(self):
        """Create a dialog for user to choose next action"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Choose Action")
        
        # Center the dialog
        dialog.geometry("300x150")
        dialog_x = self.root.winfo_x() + (self.root.winfo_width() - 300) // 2
        dialog_y = self.root.winfo_y() + (self.root.winfo_height() - 150) // 2
        dialog.geometry(f"+{dialog_x}+{dialog_y}")
        
        # Make it modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Style
        dialog.configure(bg=self.DARK_GREY)
        
        # Message
        tk.Label(
            dialog,
            text="What would you like to do?",
            bg=self.DARK_GREY,
            fg=self.TEXT_COLOR,
            font=self.HEADER_FONT
        ).pack(pady=10)
        
        # Buttons frame
        button_frame = tk.Frame(dialog, bg=self.DARK_GREY)
        button_frame.pack(expand=True)
        
        # Buttons
        ttk.Button(
            button_frame,
            text="Select Folder to Rename",
            style='Control.TButton',
            command=lambda: [dialog.destroy(), self.select_folder()]
        ).pack(pady=5)
        
        ttk.Button(
            button_frame,
            text="Create Text File",
            style='Control.TButton',
            command=lambda: [dialog.destroy(), self.create_text_file()]
        ).pack(pady=5)

    def select_folder(self):
        """Open folder selection dialog and process the selected folder"""
        folder_path = filedialog.askdirectory(
            title="Select Folder Containing Audio Files"
        )
        
        if folder_path:
            self.folder_path = folder_path
            # Check if folder contains audio files
            audio_files = [f for f in os.listdir(folder_path) 
                          if f.lower().endswith(('.wav', '.aif', '.aiff', '.mp3'))]
            
            if audio_files:
                # Update preview with the files that will be renamed
                self.preview_text.config(state='normal')
                self.preview_text.delete(1.0, tk.END)
                
                base_name = self.name_entry.get().strip()
                for file in sorted(audio_files):
                    midi_num, note_name = self.note_extractor.extract_note_from_filename(file)
                    if midi_num is not None:
                        new_name_with_extension = f"{midi_num}_{note_name}_{base_name}.wav"
                        new_name_without_extension = os.path.splitext(new_name_with_extension)[0]
                        self.preview_text.insert(tk.END, f"{file} -> {new_name_without_extension}\n")
                
                self.preview_text.config(state='disabled')
                
                # Change Submit button text and command to handle renaming
                self.submit_button.config(
                    text="Rename",
                    command=self.rename_audio_files  # Change the command to rename_audio_files
                )

    def rename_audio_files(self):
        """Rename the audio files in the selected folder"""
        try:
            base_name = self.name_entry.get().strip()
            renamed_count = 0
            errors = []
            
            # Create a backup folder
            backup_folder = os.path.join(self.folder_path, "backup")
            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)
            
            # Process each audio file
            for filename in os.listdir(self.folder_path):
                if filename.lower().endswith(('.wav', '.aif', '.aiff', '.mp3')):
                    try:
                        print(f"Processing file: {filename}")
                        
                        # Extract MIDI number and note name
                        midi_num, note_name = self.note_extractor.extract_note_from_filename(filename)
                        
                        if midi_num is not None and note_name is not None:
                            # Extract the original file extension
                            file_extension = os.path.splitext(filename)[1]  # Get the original extension
                            new_name = f"{midi_num}_{note_name}_{base_name}{file_extension}"  # Append the original extension
                            print(f"New name will be: {new_name}")
                            
                            # Check if the new filename already exists
                            if os.path.exists(os.path.join(self.folder_path, new_name)):
                                errors.append(f"File {new_name} already exists. Skipping.")
                                continue
                            
                            # Create backup
                            shutil.copy2(
                                os.path.join(self.folder_path, filename),
                                os.path.join(backup_folder, filename)
                            )
                            
                            # Rename file
                            os.rename(
                                os.path.join(self.folder_path, filename),
                                os.path.join(self.folder_path, new_name)
                            )
                            renamed_count += 1
                        else:
                            print(f"Skipping {filename}: Could not extract MIDI number or note name.")
                            errors.append(f"Could not process {filename}: Invalid format")
                
                    except Exception as e:
                        print(f"Error processing {filename}: {str(e)}")
                        errors.append(f"Error processing {filename}: {str(e)}")

        except Exception as e:
            print(f"Error in rename_audio_files: {str(e)}")
            errors.append(f"Error in rename_audio_files: {str(e)}")

# Run the GUI application
if __name__ == "__main__":
    root = tk.Tk()
    app = AudioFileRenamerTextFileGenerator(root)
    root.mainloop()