# Cool Python Projects Collection

A collection of fun, interactive Python projects ranging from audio tools to generative art, physics simulations, and terminal-based visualizations.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/arxel2468/Cool_Python
cd Cool_Python
```

2. Set up a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## System Requirements

Some projects require additional system dependencies:
- **For audio-related projects (AIBeatboxJammer, Audio-Responsive-Art):**
  - Ubuntu/Debian: `sudo apt-get install python3-dev libasound2-dev portaudio19-dev ffmpeg`
  - Arch Linux: `sudo pacman -S python-pyaudio portaudio ffmpeg`
  - Windows: Install PyAudio from a wheel if pip installation fails
- **For graphics-intensive projects:**
  - Ensure you have proper OpenGL drivers installed
  - For 3D projects, a dedicated GPU is recommended

## Projects

### AIBeatboxJammer
An interactive beatbox and loop creation tool that lets you record samples with your voice and arrange them into musical patterns.

**Features:**
- Record audio samples through your microphone
- Process samples with audio effects based on sound type (kick, snare, hi-hat)
- Create beat patterns using simple "x" and "." notation
- Play back multiple loops together for a complete beat
- Adjust tempo with BPM controls

**Usage:**
```bash
python AIBeatboxJammer.py
```

### HackerTyper
A fun terminal-based hacker simulator that makes you feel like you're in a movie hacking scene.

**Features:**
- Mash keys to generate realistic-looking code
- Type "hack" to trigger a theatrical hacking sequence
- Matrix-style visual effects and animations
- Random "Access Granted" popups and alerts
- Special commands like "matrix", "decrypt", and "help"

**Usage:**
```bash
python HackerTyper.py
```

### PhysicsSandbox
A simple 2D physics playground built with pygame and pymunk.

**Features:**
- Click to create balls with randomized colors
- Drag objects to move them around
- Watch real-time physics simulation with gravity and collisions

**Usage:**
```bash
python PhysicsSandbox.py
```

### RetroLEDScroller
A terminal-based LED sign simulator that displays scrolling text in a retro LED font.

**Features:**
- ASCII art LED font with custom characters
- Colorful scrolling animation
- Random glitch and blink effects for a retro feel

**Usage:**
```bash
python RetroLEDScroller.py
```

### Text-Adventure-Game-with-NLP
An advanced text adventure game that uses natural language processing to understand player commands.

**Features:**
- Rich storytelling with branching narratives
- Natural language command processing
- Dynamic world that responds to player actions

**Usage:**
```bash
python Text-Adventure-Game-with-NLP.py
```

### Polygon-Physics
Advanced physics simulation with support for complex polygonal objects.

**Features:**
- Create various polygon shapes
- Advanced collision detection and resolution
- Realistic physics properties including friction and elasticity

**Usage:**
```bash
python Polygon-Physics.py
```

### MouseVisual
Creates visual effects that follow mouse movements.

**Features:**
- Particle effects that track mouse position
- Customizable visual styles
- Interactive animations

**Usage:**
```bash
python MouseVisual.py
```

### GenerativeArtStudio
A creative tool for producing algorithmic art.

**Features:**
- Multiple generation algorithms
- Customizable parameters
- Export options for created art

**Usage:**
```bash
python GenerateArtStudio.py
```

### DigitalMemoryGarden
A digital garden application for organizing thoughts and ideas.

**Usage:**
```bash
python DigitalMemoryGarden.py
```

### Audio-Responsive-Art
Visual art that dynamically responds to audio input.

**Features:**
- Microphone input analysis
- Real-time visualization of audio frequencies
- Customizable visual representations

**Usage:**
```bash
python Audio-Responsive-Art.py
```

### 3D-Weather-Visualization-Globe
Visualize global weather data on a 3D Earth model.

**Features:**
- Real-time weather data visualization
- Interactive 3D globe
- Temperature, pressure, and precipitation mapping

**Usage:**
```bash
python 3D-Weather-Visualization-Globe.py
```

## Project Structure

```
.
├── samples/                      # Output directory for AIBeatboxJammer
├── output/                       # Generated output files
├── GenerativeArtStudio/          # Components for art generation
├── .venv/                        # Virtual environment (not tracked)
├── AIBeatboxJammer.py            # Audio looping and beatbox tool
├── HackerTyper.py                # Hacker simulator
├── PhysicsSandbox.py             # 2D physics sandbox
├── RetroLEDScroller.py           # Terminal LED sign simulator
├── Text-Adventure-Game-with-NLP.py
├── Polygon-Physics.py
├── MouseVisual.py
├── GenerateArtStudio.py
├── DigitalMemoryGarden.py
├── Audio-Responsive-Art.py
├── 3D-Weather-Visualization-Globe.py
├── memories.json                 # Data file for DigitalMemoryGarden
├── requirements.txt              # Project dependencies
└── README.md                     # This file
```

## Troubleshooting

### Audio Issues
- Ensure your microphone is properly connected and set as the default input device
- Check system permissions for microphone access
- For PyAudio errors:
  - On Linux: Install PortAudio development libraries
  - On Windows: Try installing PyAudio from a wheel: `pip install pipwin && pipwin install pyaudio`

### Display Issues
- For terminal-based projects (HackerTyper, RetroLEDScroller):
  - Ensure your terminal supports ANSI color codes
  - On Windows, consider using Windows Terminal instead of CMD
- For pygame projects:
  - Update your display drivers
  - Ensure you have the required resolution available (minimum 900x600)

### Performance Issues
- 3D projects may run slowly on computers without dedicated graphics
- For physics simulations, reduce the number of objects if performance suffers
