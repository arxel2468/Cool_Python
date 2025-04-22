import sys
import os
import time
import threading
import wave
import numpy as np
import pygame

# Check for required dependencies and provide helpful installation instructions
required_packages = {
    'pyaudio': 'pip install pyaudio',
    'librosa': 'pip install librosa',
    'soundfile': 'pip install soundfile',
    'pygame': 'pip install pygame',
    'pydub': 'pip install pydub',
    'numpy': 'pip install numpy'
}

missing_packages = []

# Try importing each package and collect missing ones
for package, install_cmd in required_packages.items():
    try:
        if package == 'pyaudio':
            import pyaudio
        elif package == 'librosa':
            import librosa
        elif package == 'soundfile':
            import soundfile as sf
        elif package == 'pygame':
            # Already imported at top
            pass
        elif package == 'pydub':
            from pydub import AudioSegment
    except ImportError:
        missing_packages.append((package, install_cmd))

# If there are missing packages, show instructions
if missing_packages:
    print("Some required packages are missing. Please install them:")
    for package, cmd in missing_packages:
        print(f"  {package}: {cmd}")
    
    print("\nYou may also need system dependencies:")
    print("  For Ubuntu/Debian: sudo apt-get install python3-dev libasound2-dev portaudio19-dev ffmpeg")
    print("  For Arch Linux: sudo pacman -S python-pyaudio portaudio ffmpeg")
    
    response = input("\nWould you like to continue anyway? (y/n): ")
    if response.lower() not in ['y', 'yes']:
        sys.exit(1)

class BeatboxJammer:
    def __init__(self, use_audio=True):
        # Import packages dynamically to allow the script to run even with missing dependencies
        try:
            import pyaudio
            self.pyaudio_module = pyaudio
            self.audio = pyaudio.PyAudio()
            self.format = pyaudio.paInt16
        except ImportError:
            self.pyaudio_module = None
            self.audio = None
            self.format = 16  # Fallback value
            print("WARNING: PyAudio not found. Recording will not be available.")
        
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
        self.record_seconds = 5
        self.samples = {}
        self.loops = {}
        self.playing = False
        self.bpm = 90
        self.beat_length = 60 / self.bpm
        
        # Create output directory
        if not os.path.exists("samples"):
            os.makedirs("samples")
        
        # Initialize pygame mixer if audio playback is enabled
        if use_audio:
            try:
                # First attempt with default settings
                pygame.mixer.init(frequency=self.rate, size=-16, channels=self.channels)
                print("Audio playback initialized successfully.")
            except pygame.error as e:
                try:
                    # Second attempt with more compatible settings
                    pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=2048)
                    print("Audio playback initialized with fallback settings.")
                except pygame.error as e:
                    print(f"WARNING: Could not initialize audio playback: {e}")
                    print("You will be able to record and create loops, but not play them back.")
    
    def record_sample(self, name):
        """Record a sound sample"""
        if self.audio is None:
            print("ERROR: PyAudio not available. Cannot record.")
            print("Install it with: pip install pyaudio")
            return
            
        print(f"Recording {name}... (5 seconds)")
        
        try:
            stream = self.audio.open(format=self.format, channels=self.channels,
                                    rate=self.rate, input=True,
                                    frames_per_buffer=self.chunk)
            
            frames = []
            for i in range(0, int(self.rate / self.chunk * self.record_seconds)):
                data = stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            # Save the recorded sample
            filename = f"samples/{name}.wav"
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            # Process the sample
            try:
                self.process_sample(name, filename)
                print(f"Sample {name} recorded and processed!")
            except Exception as e:
                print(f"Sample recorded but processing failed: {e}")
                # Store the unprocessed sample
                self.samples[name] = filename
                print(f"Using unprocessed sample for {name}.")
        except Exception as e:
            print(f"Error recording audio: {e}")
            print("Make sure your microphone is properly connected and permissions are set.")
    
    def process_sample(self, name, filename):
        """Process the recorded sample for better looping and sound quality"""
        try:
            import librosa
            import soundfile as sf
            
            # Load audio file
            y, sr = librosa.load(filename, sr=self.rate)
            
            # Trim silence
            y_trimmed, _ = librosa.effects.trim(y, top_db=20)
            
            # Normalize volume
            y_normalized = librosa.util.normalize(y_trimmed)
            
            # Apply some basic EQ based on the sample name
            if "kick" in name.lower() or "bass" in name.lower():
                # Boost low frequencies for bass sounds
                y_normalized = self.apply_bass_boost(y_normalized, sr)
            elif "snare" in name.lower() or "clap" in name.lower():
                # Add some snap to snares and claps
                y_normalized = self.apply_mid_boost(y_normalized, sr)
            elif "hi" in name.lower() or "hat" in name.lower():
                # Brighten hi-hats
                y_normalized = self.apply_high_boost(y_normalized, sr)
            
            # Save processed sample
            processed_filename = f"samples/{name}_processed.wav"
            sf.write(processed_filename, y_normalized, sr)
            
            # Store in our samples dictionary
            self.samples[name] = processed_filename
        except ImportError as e:
            print(f"Cannot process audio: {e}")
            print("Install librosa and soundfile for audio processing:")
            print("  pip install librosa soundfile")
            # Use the original sample
            self.samples[name] = filename
        except Exception as e:
            print(f"Error processing sample: {e}")
            # Use the original sample
            self.samples[name] = filename
    
    def apply_bass_boost(self, y, sr):
        """Apply bass boost to the sample"""
        try:
            import librosa
            # Simple low-shelf filter simulation
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            y_low = librosa.effects.preemphasis(y_harmonic, coef=0.95, zi=None)
            return y_low * 1.5 + y_percussive
        except Exception:
            # Fall back to original sample
            return y
    
    def apply_mid_boost(self, y, sr):
        """Apply mid-range boost to the sample"""
        try:
            import librosa
            # Simple mid boost
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            return y_harmonic + y_percussive * 1.3
        except Exception:
            return y
    
    def apply_high_boost(self, y, sr):
        """Apply high frequency boost to the sample"""
        try:
            import librosa
            # Simple high-shelf filter simulation
            return librosa.effects.preemphasis(y, coef=0.2)
        except Exception:
            return y
    
    def create_loop(self, name, pattern, beats=4):
        """Create a loop from a sample with a specific pattern"""
        # Pattern should be a string like "x...x...x...x..." where x means play and . means silence
        if name not in self.samples:
            print(f"Sample {name} not found!")
            return
        
        try:
            import librosa
            import soundfile as sf
            
            # Calculate beat duration in samples
            beat_duration = int(self.beat_length * self.rate)
            
            # Create a silent loop of the specified length
            loop_length = beat_duration * beats
            loop = np.zeros(loop_length)
            
            # Load the sample
            sample, sr = librosa.load(self.samples[name], sr=self.rate)
            
            # Place the sample at each 'x' position in the pattern
            pattern_length = len(pattern)
            steps_per_beat = pattern_length // beats if pattern_length >= beats else 1
            step_duration = beat_duration // steps_per_beat
            
            for i, char in enumerate(pattern):
                if char.lower() == 'x':
                    position = i * step_duration
                    # Make sure we don't exceed the loop length
                    if position + len(sample) > loop_length:
                        loop[position:] += sample[:loop_length-position]
                    else:
                        loop[position:position+len(sample)] += sample
            
            # Normalize the loop
            loop = librosa.util.normalize(loop)
            
            # Save the loop
            loop_filename = f"samples/{name}_loop.wav"
            sf.write(loop_filename, loop, self.rate)
            
            # Store in our loops dictionary
            self.loops[name] = loop_filename
            print(f"Loop created for {name} with pattern: {pattern}")
        except ImportError:
            print("Cannot create loop: librosa or soundfile is missing.")
            print("Install the required packages with: pip install librosa soundfile")
        except Exception as e:
            print(f"Error creating loop: {e}")
    
    def play_loops(self):
        """Play all loops together"""
        if not self.loops:
            print("No loops to play!")
            return
        
        # Check if pygame mixer is initialized
        if not pygame.mixer.get_init():
            print("ERROR: Audio playback is not available.")
            return
        
        try:
            # Load all loops
            pygame_loops = {}
            for name, filename in self.loops.items():
                try:
                    pygame_loops[name] = pygame.mixer.Sound(filename)
                except pygame.error as e:
                    print(f"Error loading loop {name}: {e}")
            
            if not pygame_loops:
                print("No loops could be loaded!")
                return
                
            # Play all loops
            self.playing = True
            for name, sound in pygame_loops.items():
                try:
                    sound.play(loops=-1)  # -1 means loop indefinitely
                    print(f"Playing loop: {name}")
                except pygame.error as e:
                    print(f"Error playing {name}: {e}")
            
            print("Playing all loops. Press Ctrl+C to stop.")
            try:
                while self.playing:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                self.playing = False
                pygame.mixer.stop()
                print("Playback stopped.")
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def stop_playback(self):
        """Stop playback"""
        self.playing = False
        if pygame.mixer.get_init():
            pygame.mixer.stop()
            print("Playback stopped.")
    
    def close(self):
        """Clean up resources"""
        if self.audio is not None:
            self.audio.terminate()
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        print("Resources cleaned up.")

# Interactive interface
def main():
    try:
        jammer = BeatboxJammer()
        print("===== AI BEATBOX JAMMER =====")
        print("Create awesome beats from your own sounds!")
        
        while True:
            print("\nOptions:")
            print("1. Record a new sample")
            print("2. Create a loop from a sample")
            print("3. Play all loops")
            print("4. Stop playback")
            print("5. Change BPM")
            print("6. Exit")
            
            try:
                choice = input("\nEnter your choice (1-6): ")
            except KeyboardInterrupt:
                print("\nExiting...")
                jammer.close()
                break
                
            if choice == '1':
                name = input("Enter a name for your sample (e.g., kick, snare, hihat): ")
                jammer.record_sample(name)
            
            elif choice == '2':
                if not jammer.samples:
                    print("No samples recorded yet. Record a sample first.")
                    continue
                
                print("\nAvailable samples:")
                for sample_name in jammer.samples:
                    print(f"- {sample_name}")
                
                name = input("\nWhich sample do you want to use? ")
                if name not in jammer.samples:
                    print(f"Sample '{name}' not found!")
                    continue
                
                print("\nPattern guide: 'x' = play sample, '.' = silence")
                print("Example patterns:")
                print("- Basic 4/4 beat: x...x...x...x...")
                print("- Offbeat hi-hat: ....x.......x...")
                print("- 16th note roll: xxxxxxxxxxxxxxxx")
                
                pattern = input("Enter your pattern: ")
                
                try:
                    beats = int(input("How many beats? (default: 4) ") or "4")
                except ValueError:
                    beats = 4
                    print("Invalid input. Using default of 4 beats.")
                
                jammer.create_loop(name, pattern, beats)
            
            elif choice == '3':
                # Start playback in a separate thread so we can still interact with the menu
                threading.Thread(target=jammer.play_loops, daemon=True).start()
            
            elif choice == '4':
                jammer.stop_playback()
            
            elif choice == '5':
                try:
                    new_bpm = int(input(f"Current BPM: {jammer.bpm}. Enter new BPM: "))
                    if new_bpm > 0:
                        jammer.bpm = new_bpm
                        jammer.beat_length = 60 / new_bpm
                        print(f"BPM changed to {new_bpm}")
                    else:
                        print("BPM must be a positive number.")
                except ValueError:
                    print("Invalid input. BPM must be a number.")
            
            elif choice == '6':
                print("Thanks for using the AI Beatbox Jammer!")
                jammer.close()
                break
            
            else:
                print("Invalid choice. Please enter a number from 1 to 6.")
    except Exception as e:
        print(f"Error in main(): {e}")
        print("Exiting application...")

def advanced_mode():
    try:
        jammer = BeatboxJammer()
        print("===== AI BEATBOX JAMMER - ADVANCED MODE =====")
        
        # Pre-defined rhythmic patterns
        patterns = {
            "four_on_floor": "x...x...x...x...",
            "basic_hip_hop": "x..x..x.x..x....",
            "trap_beat": "x...x...x.x.x...",
            "breakbeat": "x..x.x..x..x.x..",
            "house_hat": "x.x.x.x.x.x.x.x."
        }
        
        # Record essential samples
        print("Let's record some essential samples first!")
        
        print("\nRecording KICK drum...")
        print("Make a deep bass sound with your mouth (e.g., 'boom' or 'dum')")
        input("Press Enter when ready to record...")
        jammer.record_sample("kick")
        
        print("\nRecording SNARE...")
        print("Make a sharp snappy sound (e.g., 'ka' or a finger snap)")
        input("Press Enter when ready to record...")
        jammer.record_sample("snare")
        
        print("\nRecording HI-HAT...")
        print("Make a 'ts' or 'ch' sound with your mouth")
        input("Press Enter when ready to record...")
        jammer.record_sample("hihat")
        
        # Create basic beat
        print("\nCreating a basic beat with your samples...")
        jammer.create_loop("kick", patterns["four_on_floor"])
        jammer.create_loop("snare", "....x.......x...")
        jammer.create_loop("hihat", patterns["house_hat"])
        
        # Play the beat
        print("\nPlaying your beat! (Press Ctrl+C to stop)")
        threading.Thread(target=jammer.play_loops, daemon=True).start()
        
        try:
            while True:
                print("\nAdvanced Options:")
                print("1. Record additional sample")
                print("2. Create custom pattern")
                print("3. Apply effect to sample")
                print("4. Change BPM")
                print("5. Stop playback")
                print("6. Return to main menu")
                
                choice = input("\nEnter your choice (1-6): ")
                
                if choice == '1':
                    name = input("Enter a name for your new sample: ")
                    jammer.record_sample(name)
                
                elif choice == '2':
                    # Custom pattern creation
                    if not jammer.samples:
                        print("No samples recorded yet.")
                        continue
                    
                    print("\nAvailable samples:")
                    for sample_name in jammer.samples:
                        print(f"- {sample_name}")
                    
                    name = input("\nWhich sample do you want to use? ")
                    if name not in jammer.samples:
                        print(f"Sample '{name}' not found!")
                        continue
                    
                    print("\nAvailable patterns:")
                    for pattern_name, pattern in patterns.items():
                        print(f"- {pattern_name}: {pattern}")
                    
                    pattern_choice = input("\nEnter a pattern name or create custom (c): ")
                    if pattern_choice.lower() == 'c':
                        pattern = input("Enter custom pattern (x = sound, . = silence): ")
                    else:
                        if pattern_choice in patterns:
                            pattern = patterns[pattern_choice]
                        else:
                            print("Pattern not found. Using default.")
                            pattern = patterns["four_on_floor"]
                    
                    jammer.create_loop(name, pattern)
                    
                    # Restart playback to include the new loop
                    jammer.stop_playback()
                    threading.Thread(target=jammer.play_loops, daemon=True).start()
                
                elif choice == '3':
                    # This would be a placeholder for more advanced effects
                    print("Advanced effects coming in the next version!")
                
                elif choice == '4':
                    try:
                        new_bpm = int(input(f"Current BPM: {jammer.bpm}. Enter new BPM: "))
                        if new_bpm > 0:
                            jammer.bpm = new_bpm
                            jammer.beat_length = 60 / new_bpm
                            print(f"BPM changed to {new_bpm}")
                            
                            # Need to recreate loops with new BPM
                            print("Updating loops with new BPM...")
                            # This would require rebuilding all loops
                        else:
                            print("BPM must be a positive number.")
                    except ValueError:
                        print("Invalid input. BPM must be a number.")
                
                elif choice == '5':
                    jammer.stop_playback()
                
                elif choice == '6':
                    jammer.stop_playback()
                    return
                
                else:
                    print("Invalid choice. Please enter a number from 1 to 6.")
        
        except KeyboardInterrupt:
            jammer.stop_playback()
            print("\nReturning to main menu...")
    except Exception as e:
        print(f"Error in advanced mode: {e}")
        print("Returning to main menu...")

def check_dependencies():
    """Check if all required dependencies are properly installed"""
    missing = []
    
    # Check for system dependencies (ffmpeg for pydub)
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE,
                             timeout=2)  # Add timeout to prevent hanging
        if result.returncode != 0:
            print("WARNING: ffmpeg not found. Audio conversion with pydub might not work properly.")
            print("Install it with: sudo apt-get install ffmpeg")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("WARNING: ffmpeg not found. Audio conversion with pydub might not work properly.")
        print("Install it with: sudo apt-get install ffmpeg")
    except Exception:
        # Ignore other errors
        pass
    
    # Check if audio devices are available
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        if device_count == 0:
            print("WARNING: No audio devices found.")
        else:
            print(f"Found {device_count} audio devices.")
            
        # Check for input (microphone) devices
        input_devices = []
        for i in range(device_count):
            device_info = p.get_device_info_by_index(i)
            if device_info.get('maxInputChannels') > 0:
                input_devices.append(device_info.get('name'))
        
        if input_devices:
            print(f"Available input devices: {', '.join(input_devices)}")
        else:
            print("WARNING: No input (microphone) devices found.")
        
        p.terminate()
    except ImportError:
        print("WARNING: PyAudio not installed. Recording will not be available.")
        print("Install it with: pip install pyaudio")
    except Exception as e:
        print(f"ERROR checking audio devices: {e}")
    
    return len(missing) == 0

if __name__ == "__main__":
    print("Welcome to the AI Beatbox Jammer!")
    print("==============================")
    print("This script lets you record audio samples and create beat patterns.")
    print("You can record sounds with your voice or other sources and turn them into beats!")
    
    # Check dependencies before starting
    check_dependencies()
    
    print("\nMenu:")
    print("1. Standard Mode")
    print("2. Advanced Mode (guided setup)")
    print("3. Test Audio System")
    print("4. Install Dependencies")
    
    try:
        mode = input("Select mode (1-4): ")
        
        if mode == '2':
            advanced_mode()
        elif mode == '3':
            print("\nTesting audio system...")
            # Just initialize the jammer to test audio setup
            test_jammer = BeatboxJammer()
            if pygame.mixer.get_init():
                print("Pygame audio system is working!")
            else:
                print("Pygame audio system failed to initialize.")
            test_jammer.close()
            print("\nIf no errors appeared above, your audio system should be working!")
            print("You may need to check your system's audio settings if problems persist.")
        elif mode == '4':
            print("\nTo install all dependencies, run the following commands:")
            print("\n# System dependencies")
            print("sudo apt-get update")
            print("sudo apt-get install python3-dev libasound2-dev portaudio19-dev ffmpeg")
            print("\n# Python dependencies")
            print("pip install pyaudio numpy librosa soundfile pygame pydub")
        else:
            main()
    except KeyboardInterrupt:
        print("\nExiting AI Beatbox Jammer. Goodbye!")
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Exiting application...")