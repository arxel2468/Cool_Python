# import pygame
# import numpy as np
# import pyaudio
# import struct
# import math
# import colorsys
# from scipy.fftpack import fft

# # Initialize Pygame
# pygame.init()
# WIDTH, HEIGHT = 1200, 800
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("Audio-Responsive Generative Art")

# # Constants
# BUFFER_SIZE = 1024
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 44100
# MAX_FREQ = 5000  # Maximum frequency to analyze
# FREQ_BANDS = 32  # Number of frequency bands to analyze

# # Initialize PyAudio
# p = pyaudio.PyAudio()
# stream = p.open(
#     format=FORMAT,
#     channels=CHANNELS,
#     rate=RATE,
#     input=True,
#     frames_per_buffer=BUFFER_SIZE
# )

# # Particle class for the visualization
# class Particle:
#     def __init__(self, x, y, size, color, speed):
#         self.x = x
#         self.y = y
#         self.size = size
#         self.color = color
#         self.speed = speed
#         self.angle = np.random.uniform(0, 2 * np.pi)
#         self.life = np.random.uniform(100, 500)
        
#     def update(self, freq_data, time):
#         # Get the frequency bin most relevant to this particle
#         freq_index = int(self.x / WIDTH * len(freq_data))
#         if freq_index >= len(freq_data):
#             freq_index = len(freq_data) - 1
            
#         # Update position based on angle and speed
#         intensity = min(freq_data[freq_index] / 100, 10)
#         self.speed = 0.5 + intensity * 2
        
#         self.x += math.cos(self.angle) * self.speed
#         self.y += math.sin(self.angle) * self.speed
        
#         # Add some perlin-like noise to the movement
#         noise_factor = 0.05
#         self.angle += noise_factor * math.sin(time * 0.001 + self.x * 0.01) * intensity
        
#         # Boundary wrap-around
#         if self.x < 0:
#             self.x = WIDTH
#         elif self.x > WIDTH:
#             self.x = 0
#         if self.y < 0:
#             self.y = HEIGHT
#         elif self.y > HEIGHT:
#             self.y = 0
            
#         # Update color based on position and frequency data
#         hue = (self.x / WIDTH + time * 0.0001) % 1.0
#         saturation = 0.8 + (intensity * 0.2)
#         value = 0.7 + (intensity * 0.3)
#         r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
#         self.color = (int(r * 255), int(g * 255), int(b * 255))
        
#         # Decrease life
#         self.life -= 1
#         self.size = max(1, self.size * 0.995)
        
#     def draw(self, surface):
#         pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))
        
#         # Add a glow effect
#         for i in range(3):
#             size = self.size * (1 + i * 0.5)
#             alpha = 100 - i * 30
#             s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
#             pygame.draw.circle(s, (*self.color, alpha), (size, size), size)
#             surface.blit(s, (self.x - size, self.y - size), special_flags=pygame.BLEND_ADD)

# # Function to analyze audio and extract frequency data
# def get_audio_data():
#     data = stream.read(BUFFER_SIZE, exception_on_overflow=False)
#     data_int = struct.unpack(str(BUFFER_SIZE) + 'h', data)
#     data_np = np.array(data_int, dtype='h') / 32768.0  # Normalize to [-1, 1]
    
#     # Perform FFT
#     fft_data = fft(data_np)
#     fft_data = np.abs(fft_data[0:BUFFER_SIZE//2]) / (BUFFER_SIZE//2)
    
#     # Map to logarithmic frequency scale to match human hearing
#     freq_data = np.zeros(FREQ_BANDS)
#     for i in range(FREQ_BANDS):
#         # Logarithmic scaling - more detail in low frequencies
#         low = int(BUFFER_SIZE/2 * math.pow(2, i * math.log(MAX_FREQ/20.0) / (FREQ_BANDS * math.log(2))) / RATE * BUFFER_SIZE)
#         high = int(BUFFER_SIZE/2 * math.pow(2, (i+1) * math.log(MAX_FREQ/20.0) / (FREQ_BANDS * math.log(2))) / RATE * BUFFER_SIZE)
#         low = max(0, min(low, BUFFER_SIZE//2))
#         high = max(0, min(high, BUFFER_SIZE//2))
        
#         if high > low:
#             freq_data[i] = np.mean(fft_data[low:high]) * 100
    
#     # Apply some smoothing
#     freq_data = np.clip(freq_data, 0, 20)  # Clamp values
#     return freq_data

# # Main visualization parameters
# particles = []
# max_particles = 300
# background_alpha = 20  # For trails effect
# time = 0

# # Create surface with alpha for trails
# background = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
# background.fill((0, 0, 0, background_alpha))

# # Main loop
# running = True
# clock = pygame.time.Clock()

# while running:
#     # Handle events
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         elif event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_ESCAPE:
#                 running = False
#             elif event.key == pygame.K_SPACE:
#                 particles = []  # Reset particles
    
#     # Get audio data
#     freq_data = get_audio_data()
    
#     # Increase time counter
#     time += 1
    
#     # Apply fading trail effect
#     screen.blit(background, (0, 0))
    
#     # Update and draw particles
#     particles = [p for p in particles if p.life > 0]
#     for particle in particles:
#         particle.update(freq_data, time)
#         particle.draw(screen)
    
#     # Spawn new particles based on audio intensity
#     avg_intensity = np.mean(freq_data)
#     if len(particles) < max_particles and np.random.random() < avg_intensity * 0.1:
#         # Create particles in areas with high frequency content
#         for _ in range(int(avg_intensity)):
#             if len(particles) >= max_particles:
#                 break
                
#             # Find a frequency bin with high amplitude
#             freq_index = np.random.choice(range(len(freq_data)), p=freq_data/np.sum(freq_data))
#             x = WIDTH * freq_index / len(freq_data)
#             y = np.random.uniform(0, HEIGHT)
            
#             # Size based on frequency amplitude
#             size = 5 + freq_data[freq_index] * 2
            
#             # Initial color based on frequency (lower frequencies are redder)
#             hue = freq_index / len(freq_data)
#             r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
#             color = (int(r * 255), int(g * 255), int(b * 255))
            
#             particles.append(Particle(x, y, size, color, 1 + avg_intensity))
    
#     # Display spectrum analyzer at the bottom
#     spectrum_height = 100
#     bar_width = WIDTH / FREQ_BANDS
#     for i, amplitude in enumerate(freq_data):
#         bar_height = min(spectrum_height, amplitude * 5)
#         hue = i / FREQ_BANDS
#         r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
#         color = (int(r * 255), int(g * 255), int(b * 255))
#         pygame.draw.rect(screen, color, 
#                          (i * bar_width, HEIGHT - bar_height, bar_width, bar_height))
    
#     # Update display
#     pygame.display.flip()
#     clock.tick(60)

# # Clean up
# stream.stop_stream()
# stream.close()
# p.terminate()
# pygame.quit()


import pygame
import numpy as np
import pyaudio
import struct
import math
import colorsys
import random
import time
from collections import deque

# Audio settings
CHUNK = 1024 * 2
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Audio Responsive Generative Art")
clock = pygame.time.Clock()

# Colors
def get_color_palette():
    palettes = [
        [(46, 52, 64), (59, 66, 82), (67, 76, 94), (76, 86, 106)],  # Dark blues
        [(143, 188, 187), (69, 173, 168), (80, 250, 123), (255, 184, 108)],  # Teal and orange
        [(255, 89, 94), (255, 202, 58), (138, 201, 38), (25, 130, 196)],  # Bright primary
        [(106, 76, 147), (177, 78, 181), (220, 66, 106), (255, 84, 79)]   # Purple to orange
    ]
    return random.choice(palettes)

COLOR_PALETTE = get_color_palette()
BG_COLOR = (10, 10, 15)

# Audio visualization settings
audio_data = np.zeros(CHUNK)
prev_audio_data = np.zeros(CHUNK)
audio_history = deque(maxlen=100)
smoothed_volume = 0
bass_energy = 0
mid_energy = 0
high_energy = 0

# Particle system
class Particle:
    def __init__(self, x, y, size, color, speed, angle, life=100):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.speed = speed
        self.angle = angle
        self.life = life
        self.alpha = 255
        self.decay = random.uniform(0.95, 0.99)
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.life -= 1
        self.size *= self.decay
        self.alpha = int(255 * (self.life / 100))
        
    def draw(self, surface):
        if self.alpha > 0:
            color_with_alpha = (*self.color, self.alpha)
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color_with_alpha, (self.size, self.size), self.size)
            surface.blit(surf, (int(self.x - self.size), int(self.y - self.size)))
            
    def is_alive(self):
        return self.life > 0 and self.size > 0.5

# Harmonic waves
class HarmonicWave:
    def __init__(self, amplitude=50, frequency=0.01, phase=0, color=(255, 255, 255)):
        self.amplitude = amplitude
        self.frequency = frequency
        self.phase = phase
        self.color = color
        self.points = []
        self.line_width = 2
        
    def update(self, volume):
        self.amplitude = 30 + volume * 100
        self.phase += 0.02
        
    def draw(self, surface, y_offset, audio_data_slice):
        points = []
        for x in range(0, WIDTH, 5):
            # Use audio data to modulate the wave
            idx = int((x / WIDTH) * len(audio_data_slice))
            audio_value = audio_data_slice[idx] if idx < len(audio_data_slice) else 0
            
            y = y_offset + math.sin(x * self.frequency + self.phase) * self.amplitude
            y += audio_value * 0.5  # Add audio influence
            points.append((x, y))
            
        if len(points) > 1:
            pygame.draw.lines(surface, self.color, False, points, self.line_width)
            
        return points

# Circular patterns
class CircularPattern:
    def __init__(self, cx, cy, radius, num_points=100):
        self.cx = cx
        self.cy = cy
        self.base_radius = radius
        self.radius = radius
        self.num_points = num_points
        self.rotation = 0
        self.points = []
        self.color = random.choice(COLOR_PALETTE)
        self.line_width = 2
        self.time = 0
        self.frequency = random.uniform(1, 5)
        self.harmonics = [random.uniform(1, 10) for _ in range(3)]
        
    def update(self, volume, bass, mid, high):
        self.time += 0.01
        self.rotation += 0.005
        
        # Respond to audio features
        self.radius = self.base_radius * (1 + volume * 0.5)
        self.line_width = max(1, int(2 + volume * 5))
        
        # Update points based on harmonics and audio
        self.points = []
        for i in range(self.num_points):
            angle = (i / self.num_points) * math.pi * 2 + self.rotation
            
            # Create complex patterns using harmonics
            r = self.radius
            for j, harmonic in enumerate(self.harmonics):
                if j == 0:
                    r += math.sin(angle * harmonic + self.time) * (10 + bass * 20)
                elif j == 1:
                    r += math.cos(angle * harmonic + self.time * 1.5) * (5 + mid * 15)
                else:
                    r += math.sin(angle * harmonic * 2 + self.time * 0.7) * (3 + high * 10)
            
            x = self.cx + math.cos(angle) * r
            y = self.cy + math.sin(angle) * r
            self.points.append((x, y))
            
    def draw(self, surface):
        if len(self.points) > 2:
            # Draw the pattern with gradual color shifts
            points_closed = self.points + [self.points[0]]  # Close the loop
            
            for i in range(len(self.points)):
                # Shift hue based on position
                hue_shift = (i / len(self.points)) * 0.2 + self.time * 0.1
                r, g, b = self.color
                h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
                h = (h + hue_shift) % 1.0
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                color = (int(r*255), int(g*255), int(b*255))
                
                # Draw line segment
                start = self.points[i]
                end = self.points[(i+1) % len(self.points)]
                pygame.draw.line(surface, color, start, end, self.line_width)

# Flow fields
class FlowField:
    def __init__(self, resolution):
        self.resolution = resolution
        self.cols = WIDTH // resolution
        self.rows = HEIGHT // resolution
        self.field = np.zeros((self.cols, self.rows), dtype=float)
        self.z_offset = 0
        
    def update(self, volume):
        noise_scale = 0.1
        self.z_offset += 0.01
        
        for y in range(self.rows):
            for x in range(self.cols):
                # Perlin noise would be ideal here, but we'll use a simple approximation
                angle = (math.sin(x * noise_scale) + math.cos(y * noise_scale) + math.sin(self.z_offset)) * math.pi * 2
                self.field[x, y] = angle
                
    def get_angle(self, x, y):
        col = int(x / self.resolution)
        row = int(y / self.resolution)
        
        # Ensure indices are within bounds
        col = max(0, min(col, self.cols - 1))
        row = max(0, min(row, self.rows - 1))
        
        return self.field[col, row]
        
    def draw_debug(self, surface):
        for y in range(self.rows):
            for x in range(self.cols):
                angle = self.field[x, y]
                cx = x * self.resolution + self.resolution // 2
                cy = y * self.resolution + self.resolution // 2
                line_len = self.resolution * 0.5
                
                end_x = cx + math.cos(angle) * line_len
                end_y = cy + math.sin(angle) * line_len
                
                pygame.draw.line(surface, (100, 100, 100, 50), (cx, cy), (end_x, end_y), 1)

# Create visualization objects
particles = []
waves = [
    HarmonicWave(amplitude=50, frequency=0.01, phase=0, color=COLOR_PALETTE[0]),
    HarmonicWave(amplitude=40, frequency=0.02, phase=math.pi/2, color=COLOR_PALETTE[1]),
    HarmonicWave(amplitude=30, frequency=0.03, phase=math.pi, color=COLOR_PALETTE[2])
]
flow_field = FlowField(20)
patterns = [
    CircularPattern(WIDTH//2, HEIGHT//2, 150, num_points=150),
    CircularPattern(WIDTH//4, HEIGHT//2, 100, num_points=120),
    CircularPattern(3*WIDTH//4, HEIGHT//2, 100, num_points=120)
]

# Main loop
running = True
frame_count = 0
spawn_cooldown = 0
last_beat_time = 0
is_beat = False

# Render surface for trails
trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

def get_audio_features():
    global audio_data, prev_audio_data, smoothed_volume, bass_energy, mid_energy, high_energy
    
    # Get audio data
    data = stream.read(CHUNK, exception_on_overflow=False)
    audio_data = np.frombuffer(data, dtype=np.int16) / 32768.0  # Normalize to [-1, 1]
    
    # Calculate volume (RMS)
    volume = np.sqrt(np.mean(audio_data**2))
    smoothed_volume = smoothed_volume * 0.7 + volume * 0.3
    
    # Simple spectral analysis
    fft_data = np.abs(np.fft.fft(audio_data)[:CHUNK//2])
    
    # Divide into frequency bands (very simplified)
    bass = np.mean(fft_data[2:20])  # 20-200 Hz approx
    mid = np.mean(fft_data[20:200])  # 200-2000 Hz approx
    high = np.mean(fft_data[200:])  # 2000+ Hz
    
    # Smooth the energy values
    bass_energy = bass_energy * 0.8 + bass * 0.2
    mid_energy = mid_energy * 0.8 + mid * 0.2
    high_energy = high_energy * 0.8 + high * 0.2
    
    # Normalize energy values
    max_val = max(bass_energy, mid_energy, high_energy, 0.001)
    bass_energy_norm = bass_energy / max_val
    mid_energy_norm = mid_energy / max_val
    high_energy_norm = high_energy / max_val
    
    # Store history for beat detection
    audio_history.append(volume)
    
    # Simple beat detection
    is_beat = False
    if len(audio_history) >= 20:
        local_avg = sum(list(audio_history)[-20:]) / 20
        if volume > local_avg * 1.2 and time.time() - last_beat_time > 0.2:
            is_beat = True
            last_beat_time = time.time()
    
    prev_audio_data = audio_data.copy()
    
    return smoothed_volume, bass_energy_norm, mid_energy_norm, high_energy_norm, is_beat

# Visualization mode
mode = "all"  # "particles", "waves", "patterns", "flow", "all"
mode_change_time = 0

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                # Change visualization mode
                modes = ["particles", "waves", "patterns", "flow", "all"]
                mode = modes[(modes.index(mode) + 1) % len(modes)]
                mode_change_time = time.time()
                # Change color palette
                COLOR_PALETTE = get_color_palette()
                for wave in waves:
                    wave.color = random.choice(COLOR_PALETTE)
                for pattern in patterns:
                    pattern.color = random.choice(COLOR_PALETTE)
    
    # Get audio data and features
    volume, bass, mid, high, is_beat = get_audio_features()
    
    # Clear screen with fade effect for trails
    screen.fill(BG_COLOR)
    trail_surface.fill((0, 0, 0, 5))  # Fade out previous frame
    
    # Update flow field
    flow_field.update(volume)
    
    # Update particles
    if frame_count % 2 == 0 and (mode == "particles" or mode == "all"):
        # Add new particles on beat or regularly based on volume
        if is_beat or spawn_cooldown <= 0:
            num_particles = int(10 + volume * 50)
            spawn_cooldown = 5
            
            if is_beat:
                # Create a burst of particles on beat
                for _ in range(num_particles * 2):
                    x = random.randint(WIDTH//4, 3*WIDTH//4)
                    y = random.randint(HEIGHT//4, 3*HEIGHT//4)
                    size = random.uniform(3, 10)
                    color = random.choice(COLOR_PALETTE)
                    speed = random.uniform(1, 5) * (1 + volume)
                    angle = random.uniform(0, math.pi * 2)
                    particles.append(Particle(x, y, size, color, speed, angle))
            else:
                # Regular particle emission
                for _ in range(max(1, int(num_particles * 0.2))):
                    x = random.randint(0, WIDTH)
                    y = random.randint(0, HEIGHT)
                    size = random.uniform(2, 6)
                    color = random.choice(COLOR_PALETTE)
                    
                    # Get flow direction from flow field
                    angle = flow_field.get_angle(x, y)
                    speed = random.uniform(0.5, 2) * (1 + volume)
                    
                    particles.append(Particle(x, y, size, color, speed, angle))
        
        spawn_cooldown -= 1
    
    # Update and draw particles
    if mode == "particles" or mode == "all" or mode == "flow":
        for p in particles[:]:
            p.update()
            
            # Apply flow field influence
            if mode == "flow" or (mode == "all" and random.random() < 0.2):
                flow_angle = flow_field.get_angle(p.x, p.y)
                # Blend current direction with flow field
                p.angle = p.angle * 0.95 + flow_angle * 0.05
                
            p.draw(trail_surface)
            if not p.is_alive():
                particles.remove(p)
    
    # Debug: flow field visualization
    if mode == "flow" and frame_count % 20 == 0:
        flow_field.draw_debug(screen)
    
    # Update and draw waves
    if mode == "waves" or mode == "all":
        wave_points = []
        for i, wave in enumerate(waves):
            wave.update(volume)
            y_offset = HEIGHT * (i + 1) / (len(waves) + 1)
            
            # Use different frequency bands for different waves
            if i == 0:
                audio_slice = audio_data[:CHUNK//3] * (1 + bass * 3)
            elif i == 1:
                audio_slice = audio_data[CHUNK//3:2*CHUNK//3] * (1 + mid * 3)
            else:
                audio_slice = audio_data[2*CHUNK//3:] * (1 + high * 3)
                
            points = wave.draw(screen, y_offset, audio_slice)
            wave_points.extend(points)
        
        # Connect wave points with lines occasionally for interesting effects
        if random.random() < 0.05 * volume:
            for _ in range(5):
                if len(wave_points) > 2:
                    p1 = random.choice(wave_points)
                    p2 = random.choice(wave_points)
                    color = random.choice(COLOR_PALETTE)
                    pygame.draw.line(trail_surface, (*color, 50), p1, p2, 1)
    
    # Update and draw circular patterns
    if mode == "patterns" or mode == "all":
        for pattern in patterns:
            pattern.update(volume, bass, mid, high)
            pattern.draw(screen)
            
            # Create particles from pattern points when there's a beat
            if is_beat and (mode == "all" or mode == "patterns"):
                for i in range(0, len(pattern.points), 5):
                    if random.random() < 0.3:
                        p = pattern.points[i]
                        size = random.uniform(2, 6)
                        color = random.choice(COLOR_PALETTE)
                        speed = random.uniform(1, 3) * (1 + volume)
                        # Particles move outward from center
                        angle = math.atan2(p[1] - pattern.cy, p[0] - pattern.cx)
                        particles.append(Particle(p[0], p[1], size, color, speed, angle))
    
    # Apply the trail surface for persistence effects
    screen.blit(trail_surface, (0, 0))
    
    # Show mode change notification
    if time.time() - mode_change_time < 2:
        font = pygame.font.Font(None, 36)
        text = font.render(f"Mode: {mode}", True, (255, 255, 255))
        screen.blit(text, (20, 20))
    
    # Show audio visualization
    pygame.draw.rect(screen, (50, 50, 50), (WIDTH-210, HEIGHT-110, 200, 100))
    
    # Volume meter
    vol_height = int(volume * 100)
    pygame.draw.rect(screen, (200, 200, 200), (WIDTH-200, HEIGHT-100, 20, 90))
    pygame.draw.rect(screen, (255, 100, 100), (WIDTH-200, HEIGHT-10-vol_height, 20, vol_height))
    
    # Frequency bands
    bar_width = 40
    pygame.draw.rect(screen, (80, 80, 200), (WIDTH-170, HEIGHT-10-int(bass*90), bar_width, int(bass*90)))
    pygame.draw.rect(screen, (80, 200, 80), (WIDTH-120, HEIGHT-10-int(mid*90), bar_width, int(mid*90)))
    pygame.draw.rect(screen, (200, 200, 80), (WIDTH-70, HEIGHT-10-int(high*90), bar_width, int(high*90)))
    
    # Display stats
    font = pygame.font.Font(None, 24)
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (200, 200, 200))
    screen.blit(fps_text, (WIDTH-100, 20))
    particle_text = font.render(f"Particles: {len(particles)}", True, (200, 200, 200))
    screen.blit(particle_text, (WIDTH-150, 50))
    
    # Update display
    pygame.display.flip()
    clock.tick(60)
    frame_count += 1

# Clean up
stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()