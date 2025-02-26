import pygame
import numpy as np
import math
import random
import colorsys
import os
from datetime import datetime

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 800
PREVIEW_WIDTH, PREVIEW_HEIGHT = 500, 400
UI_PANEL_WIDTH = 300
TOTAL_WIDTH = WIDTH + UI_PANEL_WIDTH

# Canvas setup
screen = pygame.display.set_mode((TOTAL_WIDTH, HEIGHT))
pygame.display.set_caption("Generative Art Studio")
canvas = pygame.Surface((WIDTH, HEIGHT))
preview_canvas = pygame.Surface((PREVIEW_WIDTH, PREVIEW_HEIGHT))

# UI settings
UI_BG_COLOR = (30, 30, 40)
UI_TEXT_COLOR = (230, 230, 230)
UI_ACCENT_COLOR = (100, 130, 250)
UI_BUTTON_COLOR = (60, 70, 90)
UI_BUTTON_HOVER_COLOR = (80, 90, 120)
font_small = pygame.font.SysFont("Arial", 16)
font_medium = pygame.font.SysFont("Arial", 20)
font_large = pygame.font.SysFont("Arial", 24)

# Color palettes
def generate_complementary_palette(base_hue, saturation=0.7, lightness_values=[0.3, 0.5, 0.7, 0.9]):
    palette = []
    # Base color
    r, g, b = colorsys.hls_to_rgb(base_hue, lightness_values[1], saturation)
    palette.append((int(r*255), int(g*255), int(b*255)))
    
    # Complementary color
    complementary_hue = (base_hue + 0.5) % 1.0
    r, g, b = colorsys.hls_to_rgb(complementary_hue, lightness_values[1], saturation)
    palette.append((int(r*255), int(g*255), int(b*255)))
    
    # Variations of base
    for l in lightness_values:
        r, g, b = colorsys.hls_to_rgb(base_hue, l, saturation)
        palette.append((int(r*255), int(g*255), int(b*255)))
    
    # Variations of complementary
    for l in lightness_values:
        r, g, b = colorsys.hls_to_rgb(complementary_hue, l, saturation)
        palette.append((int(r*255), int(g*255), int(b*255)))
        
    return palette

def generate_analogous_palette(base_hue, saturation=0.7, lightness=0.5, angle=0.05):
    palette = []
    hues = [base_hue, 
            (base_hue + angle) % 1.0, 
            (base_hue + 2*angle) % 1.0,
            (base_hue - angle) % 1.0, 
            (base_hue - 2*angle) % 1.0]
    
    for h in hues:
        r, g, b = colorsys.hls_to_rgb(h, lightness, saturation)
        palette.append((int(r*255), int(g*255), int(b*255)))
        
    # Add variations in lightness
    for h in [base_hue, (base_hue + angle) % 1.0]:
        for l in [0.3, 0.7]:
            r, g, b = colorsys.hls_to_rgb(h, l, saturation)
            palette.append((int(r*255), int(g*255), int(b*255)))
            
    return palette

def generate_triadic_palette(base_hue, saturation=0.7, lightness=0.5):
    palette = []
    hues = [base_hue, 
            (base_hue + 1/3) % 1.0, 
            (base_hue + 2/3) % 1.0]
    
    for h in hues:
        for l in [0.3, 0.5, 0.7]:
            r, g, b = colorsys.hls_to_rgb(h, l, saturation)
            palette.append((int(r*255), int(g*255), int(b*255)))
            
    return palette

def generate_random_palette():
    base_hue = random.random()
    palette_type = random.choice(["complementary", "analogous", "triadic"])
    
    if palette_type == "complementary":
        return generate_complementary_palette(base_hue)
    elif palette_type == "analogous":
        return generate_analogous_palette(base_hue)
    else:
        return generate_triadic_palette(base_hue)

# Mandelbrot and Julia Set Generation
def compute_mandelbrot(h, w, max_iterations, x_min, x_max, y_min, y_max):
    result = np.zeros((h, w))
    for y in range(h):
        for x in range(w):
            # Convert pixel coordinates to complex plane
            c_real = x_min + (x / w) * (x_max - x_min)
            c_imag = y_min + (y / h) * (y_max - y_min)
            c = complex(c_real, c_imag)
            
            # Initialize z and iteration counter
            z = complex(0, 0)
            n = 0
            
            # Check if point is in Mandelbrot set
            while abs(z) <= 2.0 and n < max_iterations:
                z = z**2 + c
                n += 1
                
            if n == max_iterations:
                result[y, x] = 0
            else:
                # Smooth coloring
                result[y, x] = n + 1 - np.log(np.log(abs(z))) / np.log(2)
                
    return result

def compute_julia(h, w, max_iterations, x_min, x_max, y_min, y_max, c):
    result = np.zeros((h, w))
    for y in range(h):
        for x in range(w):
            # Convert pixel coordinates to complex plane
            z_real = x_min + (x / w) * (x_max - x_min)
            z_imag = y_min + (y / h) * (y_max - y_min)
            z = complex(z_real, z_imag)
            
            # Initialize iteration counter
            n = 0
            
            # Check if point is in Julia set
            while abs(z) <= 2.0 and n < max_iterations:
                z = z**2 + c
                n += 1
                
            if n == max_iterations:
                result[y, x] = 0
            else:
                # Smooth coloring
                result[y, x] = n + 1 - np.log(np.log(abs(z))) / np.log(2)
                
    return result

def color_fractal(fractal, palette):
    h, w = fractal.shape
    surface = pygame.Surface((w, h))
    
    max_val = np.max(fractal)
    if max_val == 0:
        max_val = 1  # Avoid division by zero
        
    for y in range(h):
        for x in range(w):
            if fractal[y, x] == 0:
                # Point is in the set
                surface.set_at((x, y), (0, 0, 0))
            else:
                # Point is outside the set
                color_index = int((fractal[y, x] / max_val * (len(palette) - 1))) % len(palette)
                surface.set_at((x, y), palette[color_index])
                
    return surface

# Particle Systems
class Particle:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.ax = 0
        self.ay = 0
        self.life = 100
        self.original_size = size
        
    def apply_force(self, fx, fy):
        self.ax += fx
        self.ay += fy
        
    def update(self):
        self.vx += self.ax
        self.vy += self.ay
        self.x += self.vx
        self.y += self.vy
        self.ax = 0
        self.ay = 0
        self.life -= 1
        self.size = self.original_size * (self.life / 100)
        
    def draw(self, surface):
        if self.size > 0.5:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))
            
    def is_alive(self):
        return self.life > 0 and 0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT

class ParticleSystem:
    def __init__(self, num_particles, palette):
        self.particles = []
        self.palette = palette
        self.num_particles = num_particles
        self.emit_rate = 5
        self.frame_count = 0
        
        # Flow field settings
        self.resolution = 20
        self.cols = WIDTH // self.resolution
        self.rows = HEIGHT // self.resolution
        self.flow_field = np.zeros((self.cols, self.rows, 2))  # 2D vector field
        self.flow_z_offset = 0
        self.flow_scale = 0.1
        
        # Initialize flow field
        self.update_flow_field()
        
    def update_flow_field(self):
        self.flow_z_offset += 0.01
        for y in range(self.rows):
            for x in range(self.cols):
                # Simple "Perlin-like" noise approximation
                angle = (math.sin(x * self.flow_scale) + 
                         math.cos(y * self.flow_scale) + 
                         math.sin(self.flow_z_offset)) * math.pi * 2
                self.flow_field[x, y, 0] = math.cos(angle)
                self.flow_field[x, y, 1] = math.sin(angle)
    
    def get_flow_vector(self, x, y):
        col = int(x / self.resolution)
        row = int(y / self.resolution)
        
        # Clamp to grid boundaries
        col = max(0, min(col, self.cols - 1))
        row = max(0, min(row, self.rows - 1))
        
        return self.flow_field[col, row]
        
    def update(self):
        self.frame_count += 1
        
        # Update flow field periodically
        if self.frame_count % 10 == 0:
            self.update_flow_field()
        
        # Add new particles
        if len(self.particles) < self.num_particles:
            for _ in range(min(self.emit_rate, self.num_particles - len(self.particles))):
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
                size = random.uniform(2, 8)
                color = random.choice(self.palette)
                self.particles.append(Particle(x, y, size, color))
        
        # Update existing particles
        for p in self.particles[:]:
            # Apply flow field force
            flow_vec = self.get_flow_vector(p.x, p.y)
            p.apply_force(flow_vec[0] * 0.1, flow_vec[1] * 0.1)
            
            p.update()
            if not p.is_alive():
                self.particles.remove(p)
                
    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
            
    def draw_debug(self, surface):
        # Draw flow field vectors
        for y in range(self.rows):
            for x in range(self.cols):
                cx = x * self.resolution + self.resolution // 2
                cy = y * self.resolution + self.resolution // 2
                fx, fy = self.flow_field[x, y]
                
                pygame.draw.line(
                    surface, 
                    (100, 100, 100, 100), 
                    (cx, cy), 
                    (cx + fx * self.resolution // 2, cy + fy * self.resolution // 2),
                    1
                )

# Art Generators
class FractalGenerator:
    def __init__(self):
        self.type = "mandelbrot"
        self.max_iterations = 100
        self.x_center = -0.5
        self.y_center = 0
        self.zoom = 2.5
        self.palette = generate_random_palette()
        self.julia_c = complex(-0.7, 0.27)
        
    def update_params(self, x_center=None, y_center=None, zoom=None, max_iterations=None):
        if x_center is not None:
            self.x_center = x_center
        if y_center is not None:
            self.y_center = y_center
        if zoom is not None:
            self.zoom = zoom
        if max_iterations is not None:
            self.max_iterations = max_iterations
            
    def generate(self, width, height):
        aspect_ratio = width / height
        x_min = self.x_center - self.zoom / 2
        x_max = self.x_center + self.zoom / 2
        y_min = self.y_center - self.zoom / (2 * aspect_ratio)
        y_max = self.y_center + self.zoom / (2 * aspect_ratio)
        
        if self.type == "mandelbrot":
            fractal = compute_mandelbrot(height, width, self.max_iterations, x_min, x_max, y_min, y_max)
        else:  # julia
            fractal = compute_julia(height, width, self.max_iterations, x_min, x_max, y_min, y_max, self.julia_c)
            
        return color_fractal(fractal, self.palette)

class ParticleGenerator:
    def __init__(self):
        self.num_particles = 500
        self.palette = generate_random_palette()
        self.system = ParticleSystem(self.num_particles, self.palette)
        self.show_debug = False
        
    def update(self):
        self.system.update()
        
    def generate(self, surface):
        surface.fill((0, 0, 0))
        self.system.draw(surface)
        if self.show_debug:
            self.system.draw_debug(surface)

# UI Classes
class Button:
    def __init__(self, x, y, width, height, text, color=UI_BUTTON_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = UI_BUTTON_HOVER_COLOR
        self.text_color = UI_TEXT_COLOR
        self.font = font_medium
        
    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        
        pygame.draw.rect(surface, current_color, self.rect, border_radius=5)
        pygame.draw.rect(surface, UI_ACCENT_COLOR, self.rect, 1, border_radius=5)
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

class RadioButton:
    def __init__(self, x, y, width, height, text, value, group):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.value = value
        self.group = group
        self.selected = False
        
    def draw(self, surface):
        color = UI_ACCENT_COLOR if self.selected else UI_BUTTON_COLOR
        
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, UI_TEXT_COLOR, self.rect, 1, border_radius=5)
        
        text_surf = font_small.render(self.text, True, UI_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.text = text
        self.dragging = False
        self.handle_radius = 8
        
    def draw(self, surface):
        # Draw track
        track_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height // 2 - 2, 
                                 self.rect.width, 4)
        pygame.draw.rect(surface, (60, 60, 70), track_rect, border_radius=2)
        
        # Draw handle
        handle_x = self.rect.x + int((self.value - self.min_val) / 
                                     (self.max_val - self.min_val) * self.rect.width)
        handle_y = self.rect.y + self.rect.height // 2
        pygame.draw.circle(surface, UI_ACCENT_COLOR, (handle_x, handle_y), self.handle_radius)
        
        # Draw text and value
        text_surf = font_small.render(f"{self.text}: {self.value}", True, UI_TEXT_COLOR)
        surface.blit(text_surf, (self.rect.x, self.rect.y - 15))
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handle_x = self.rect.x + int((self.value - self.min_val) / 
                                         (self.max_val - self.min_val) * self.rect.width)
            handle_y = self.rect.y + self.rect.height // 2
            handle_rect = pygame.Rect(handle_x - self.handle_radius, 
                                      handle_y - self.handle_radius,
                                      self.handle_radius * 2, 
                                      self.handle_radius * 2)
            
            if handle_rect.collidepoint(event.pos):
                self.dragging = True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Update value based on mouse position
            pos_ratio = (event.pos[0] - self.rect.x) / self.rect.width
            pos_ratio = max(0, min(1, pos_ratio))
            self.value = self.min_val + pos_ratio * (self.max_val - self.min_val)
            
            # Round to integer if needed
            if isinstance(self.min_val, int) and isinstance(self.max_val, int):
                self.value = round(self.value)

# Application
class GenerativeArtStudio:
    def __init__(self):
        self.running = True
        self.generator_mode = "fractal"
        self.animation_frames = []
        self.recording = False
        self.frame_count = 0
        
        # Create generators
        self.fractal_gen = FractalGenerator()
        self.particle_gen = ParticleGenerator()
        
        # Create UI elements
        self.setup_ui()
        
        # Generate initial art
        self.regenerate_art()
        
    def setup_ui(self):
        self.ui_elements = []
        
        # Mode selection buttons
        self.fractal_btn = RadioButton(WIDTH + 20, 20, 120, 30, "Fractal", "fractal", "mode")
        self.particle_btn = RadioButton(WIDTH + 150, 20, 120, 30, "Particles", "particle", "mode")
        self.fractal_btn.selected = (self.generator_mode == "fractal")
        self.particle_btn.selected = (self.generator_mode == "particle")
        self.ui_elements.extend([self.fractal_btn, self.particle_btn])
        
        # Fractal controls
        y_offset = 80
        self.fractal_controls = []
        
        # Fractal type selection
        self.mandelbrot_btn = RadioButton(WIDTH + 20, y_offset, 120, 30, "Mandelbrot", "mandelbrot", "fractal_type")
        self.julia_btn = RadioButton(WIDTH + 150, y_offset, 120, 30, "Julia Set", "julia", "fractal_type")
        self.mandelbrot_btn.selected = (self.fractal_gen.type == "mandelbrot")
        self.julia_btn.selected = (self.fractal_gen.type == "julia")
        self.fractal_controls.extend([self.mandelbrot_btn, self.julia_btn])
        
        y_offset += 50
        
        # Fractal parameters
        self.iter_slider = Slider(WIDTH + 20, y_offset, 250, 20, 50, 500, self.fractal_gen.max_iterations, "Iterations")
        self.fractal_controls.append(self.iter_slider)
        
        y_offset += 40
        
        self.zoom_slider = Slider(WIDTH + 20, y_offset, 250, 20, 0.1, 4.0, self.fractal_gen.zoom, "Zoom")
        self.fractal_controls.append(self.zoom_slider)
        
        y_offset += 40
        
        if self.fractal_gen.type == "julia":
            self.julia_real_slider = Slider(WIDTH + 20, y_offset, 250, 20, -2.0, 2.0, self.fractal_gen.julia_c.real, "Julia c.real")
            self.fractal_controls.append(self.julia_real_slider)
            
            y_offset += 40
            
            self.julia_imag_slider = Slider(WIDTH + 20, y_offset, 250, 20, -2.0, 2.0, self.fractal_gen.julia_c.imag, "Julia c.imag")
            self.fractal_controls.append(self.julia_imag_slider)
            
            y_offset += 40
        
        # Particle controls
        self.particle_controls = []
        y_offset = 80
        
        self.particles_slider = Slider(WIDTH + 20, y_offset, 250, 20, 100, 2000, self.particle_gen.num_particles, "Num Particles")
        self.particle_controls.append(self.particles_slider)
        
        y_offset += 40
        
        self.debug_btn = Button(WIDTH + 20, y_offset, 250, 30, "Toggle Debug View")
        self.particle_controls.append(self.debug_btn)
        
        # General controls
        y_offset = 280
        
        self.regenerate_btn = Button(WIDTH + 20, y_offset, 250, 40, "Regenerate Art")
        self.ui_elements.append(self.regenerate_btn)
        
        y_offset += 60
        
        self.regenerate_palette_btn = Button(WIDTH + 20, y_offset, 250, 40, "New Color Palette")
        self.ui_elements.append(self.regenerate_palette_btn)
        
        y_offset += 60
        
        self.save_btn = Button(WIDTH + 20, y_offset, 250, 40, "Save Image")
        self.ui_elements.append(self.save_btn)
        
        y_offset += 60
        
        self.record_btn = Button(WIDTH + 20, y_offset, 250, 40, "Record Animation", 
                                color=(200, 60, 60) if self.recording else UI_BUTTON_COLOR)
        self.ui_elements.append(self.record_btn)
        
        y_offset += 60
        
        # Add active controls to UI elements
        if self.generator_mode == "fractal":
            self.ui_elements.extend(self.fractal_controls)
        else:
            self.ui_elements.extend(self.particle_controls)
            
    def regenerate_art(self):
        if self.generator_mode == "fractal":
            # Update fractal parameters
            self.fractal_gen.max_iterations = self.iter_slider.value
            self.fractal_gen.zoom = self.zoom_slider.value
            
            if self.fractal_gen.type == "julia":
                self.fractal_gen.julia_c = complex(self.julia_real_slider.value, self.julia_imag_slider.value)
                
            # Generate new fractal
            self.art_surface = self.fractal_gen.generate(WIDTH, HEIGHT)
            self.preview_surface = pygame.transform.scale(self.art_surface, (PREVIEW_WIDTH, PREVIEW_HEIGHT))
        else:
            # Update particle parameters
            if self.particle_gen.num_particles != self.particles_slider.value:
                self.particle_gen.num_particles = self.particles_slider.value
                self.particle_gen.system = ParticleSystem(self.particle_gen.num_particles, self.particle_gen.palette)
    
    def run(self):
        clock = pygame.time.Clock()
        
        while self.running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        
                # Handle UI events
                for element in self.ui_elements:
                    if isinstance(element, Slider):
                        element.handle_event(event)
                    elif isinstance(element, (Button, RadioButton)):
                        if element.is_clicked(event):
                            self.handle_ui_click(element)
            
            # Clear screen
            screen.fill(UI_BG_COLOR)
            
            # Update and draw art
            if self.generator_mode == "fractal":
                # Draw precomputed fractal
                screen.blit(self.art_surface, (0, 0))
            else:
                # Update particle system
                self.particle_gen.update()
                self.particle_gen.generate(canvas)
                screen.blit(canvas, (0, 0))
                
                # Update preview
                self.preview_surface = pygame.transform.scale(canvas, (PREVIEW_WIDTH, PREVIEW_HEIGHT))
            
            # Draw UI panel
            self.draw_ui()
            
            # Handle animation recording
            if self.recording:
                self.frame_count += 1
                if self.frame_count % 5 == 0:  # Save every 5th frame
                    if self.generator_mode == "fractal":
                        # For fractals, modify parameters slightly for animation
                        if self.fractal_gen.type == "mandelbrot":
                            self.fractal_gen.zoom *= 0.98  # Zoom in
                        else:  # julia
                            # Rotate Julia parameter
                            angle = 0.05
                            c = self.fractal_gen.julia_c
                            real = c.real * math.cos(angle) - c.imag * math.sin(angle)
                            imag = c.real * math.sin(angle) + c.imag * math.cos(angle)
                            self.fractal_gen.julia_c = complex(real, imag)
                            
                            # Update sliders to reflect new value
                            if hasattr(self, 'julia_real_slider'):
                                self.julia_real_slider.value = real
                            if hasattr(self, 'julia_imag_slider'):
                                self.julia_imag_slider.value = imag
                        
                        self.regenerate_art()
                    
                    # Save frame to list
                    self.animation_frames.append(canvas.copy())
                    
                    # If we've collected enough frames, stop recording
                    if len(self.animation_frames) >= 60:
                        self.save_animation()
                        self.recording = False
                        self.record_btn.color = UI_BUTTON_COLOR
                        self.record_btn.text = "Record Animation"
                        
            # Update display
            pygame.display.flip()
            clock.tick(60)
            
        pygame.quit()
        
    def draw_ui(self):
        # Draw border around art area
        pygame.draw.rect(screen, UI_ACCENT_COLOR, (0, 0, WIDTH, HEIGHT), 2)
        
        # Draw preview
        if hasattr(self, 'preview_surface'):
            preview_x = WIDTH + (UI_PANEL_WIDTH - PREVIEW_WIDTH) // 2
            preview_y = HEIGHT - PREVIEW_HEIGHT - 20
            screen.blit(self.preview_surface, (preview_x, preview_y))
            pygame.draw.rect(screen, UI_ACCENT_COLOR, 
                            (preview_x, preview_y, PREVIEW_WIDTH, PREVIEW_HEIGHT), 1)
            
            # Draw preview label
            label = font_small.render("Preview", True, UI_TEXT_COLOR)
            screen.blit(label, (preview_x, preview_y - 20))
        
        # Draw UI title
        title = font_large.render("Generative Art Studio", True, UI_TEXT_COLOR)
        screen.blit(title, (WIDTH + (UI_PANEL_WIDTH - title.get_width()) // 2, 50))
        
        # Draw mode label
        mode_label = font_medium.render("Generator Type:", True, UI_TEXT_COLOR)
        screen.blit(mode_label, (WIDTH + 20, 65))
        
        # Draw UI elements
        for element in self.ui_elements:
            element.draw(screen)
            
        # Draw recording indicator if active
        if self.recording:
            record_text = font_medium.render(f"Recording... Frame {len(self.animation_frames)}/60", 
                                           True, (255, 100, 100))
            screen.blit(record_text, (WIDTH + 20, HEIGHT - 50))
    
    def handle_ui_click(self, element):
        # Mode selection
        if element == self.fractal_btn:
            self.generator_mode = "fractal"
            self.fractal_btn.selected = True
            self.particle_btn.selected = False
            
            # Update UI elements
            self.ui_elements = [elem for elem in self.ui_elements 
                               if not elem in self.particle_controls]
            self.ui_elements.extend(self.fractal_controls)
            
            # Generate fractal art
            self.regenerate_art()
            
        elif element == self.particle_btn:
            self.generator_mode = "particle"
            self.fractal_btn.selected = False
            self.particle_btn.selected = True
            
            # Update UI elements
            self.ui_elements = [elem for elem in self.ui_elements 
                               if not elem in self.fractal_controls]
            self.ui_elements.extend(self.particle_controls)
            
        # Fractal type selection
        elif element == self.mandelbrot_btn:
            self.fractal_gen.type = "mandelbrot"
            self.mandelbrot_btn.selected = True
            self.julia_btn.selected = False
            
            # Update UI to remove Julia-specific controls
            self.ui_elements = [elem for elem in self.ui_elements 
                               if not elem in [self.julia_real_slider, self.julia_imag_slider]]
            self.fractal_controls = [elem for elem in self.fractal_controls 
                                   if not elem in [self.julia_real_slider, self.julia_imag_slider]]
            
            self.regenerate_art()
            
        elif element == self.julia_btn:
            self.fractal_gen.type = "julia"
            self.mandelbrot_btn.selected = False
            self.julia_btn.selected = True
            
            # Add Julia-specific controls
            y_offset = 160
            self.julia_real_slider = Slider(WIDTH + 20, y_offset, 250, 20, 
                                           -2.0, 2.0, self.fractal_gen.julia_c.real, 
                                           "Julia c.real")
            
            y_offset += 40
            self.julia_imag_slider = Slider(WIDTH + 20, y_offset, 250, 20, 
                                           -2.0, 2.0, self.fractal_gen.julia_c.imag, 
                                           "Julia c.imag")
            
            self.fractal_controls.extend([self.julia_real_slider, self.julia_imag_slider])
            if self.generator_mode == "fractal":
                self.ui_elements.extend([self.julia_real_slider, self.julia_imag_slider])
                
            self.regenerate_art()
            
        # Particle controls
        elif element == self.debug_btn:
            self.particle_gen.show_debug = not self.particle_gen.show_debug
            
        # General controls
        elif element == self.regenerate_btn:
            if self.generator_mode == "fractal":
                # Reset fractal view parameters
                self.fractal_gen.x_center = -0.5 if self.fractal_gen.type == "mandelbrot" else 0
                self.fractal_gen.y_center = 0
                self.fractal_gen.zoom = 2.5
                self.zoom_slider.value = 2.5
                
                if self.fractal_gen.type == "julia":
                    # Generate new Julia parameter
                    angle = random.uniform(0, math.pi * 2)
                    radius = random.uniform(0.3, 1.0)
                    self.fractal_gen.julia_c = complex(
                        radius * math.cos(angle),
                        radius * math.sin(angle)
                    )
                    self.julia_real_slider.value = self.fractal_gen.julia_c.real
                    self.julia_imag_slider.value = self.fractal_gen.julia_c.imag
                
            else:  # particle mode
                # Create new particle system
                self.particle_gen.system = ParticleSystem(
                    self.particle_gen.num_particles, 
                    self.particle_gen.palette
                )
                
            self.regenerate_art()
            
        elif element == self.regenerate_palette_btn:
            # Generate new color palette
            new_palette = generate_random_palette()
            
            if self.generator_mode == "fractal":
                self.fractal_gen.palette = new_palette
                self.regenerate_art()
            else:
                self.particle_gen.palette = new_palette
                self.particle_gen.system = ParticleSystem(
                    self.particle_gen.num_particles, 
                    new_palette
                )
                
        elif element == self.save_btn:
            self.save_image()
            
        elif element == self.record_btn:
            if not self.recording:
                self.recording = True
                self.animation_frames = []
                self.frame_count = 0
                self.record_btn.color = (200, 60, 60)
                self.record_btn.text = "Recording..."
            else:
                self.save_animation()
                self.recording = False
                self.record_btn.color = UI_BUTTON_COLOR
                self.record_btn.text = "Record Animation"
    
    def save_image(self):
        # Create output directory if it doesn't exist
        if not os.path.exists("output"):
            os.makedirs("output")
            
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        mode = "fractal" if self.generator_mode == "fractal" else "particle"
        subtype = self.fractal_gen.type if self.generator_mode == "fractal" else ""
        
        filename = f"output/generative_art_{mode}_{subtype}_{timestamp}.png"
        
        # Save the canvas
        if self.generator_mode == "fractal":
            pygame.image.save(self.art_surface, filename)
        else:
            pygame.image.save(canvas, filename)
            
        print(f"Image saved as {filename}")
        
        # Show confirmation in UI (could be improved with a proper notification system)
        self.save_btn.text = "Saved!"
        pygame.time.set_timer(pygame.USEREVENT, 1000)  # Reset text after 1 second
        
    def save_animation(self):
        if not self.animation_frames:
            return
            
        # Create output directory if it doesn't exist
        if not os.path.exists("output"):
            os.makedirs("output")
            
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        mode = "fractal" if self.generator_mode == "fractal" else "particle"
        subtype = self.fractal_gen.type if self.generator_mode == "fractal" else ""
        
        # Save individual frames
        folder_name = f"output/animation_{mode}_{subtype}_{timestamp}"
        os.makedirs(folder_name)
        
        for i, frame in enumerate(self.animation_frames):
            pygame.image.save(frame, f"{folder_name}/frame_{i:04d}.png")
            
        print(f"Animation frames saved to {folder_name}")
        print(f"You can convert these frames to a video using FFmpeg:")
        print(f"ffmpeg -framerate 30 -i {folder_name}/frame_%04d.png -c:v libx264 -pix_fmt yuv420p {folder_name}/animation.mp4")

# Additional fractal types
class FlameGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.histogram = np.zeros((height, width, 3), dtype=np.float64)
        self.num_functions = random.randint(3, 7)
        self.functions = []
        self.palette = generate_random_palette()
        self.init_functions()
        
    def init_functions(self):
        self.functions = []
        for _ in range(self.num_functions):
            # Each function is a dict with coefficients for affine transform
            # and color weight
            function = {
                'a': random.uniform(-1, 1),
                'b': random.uniform(-1, 1),
                'c': random.uniform(-1, 1),
                'd': random.uniform(-1, 1),
                'e': random.uniform(-1, 1),
                'f': random.uniform(-1, 1),
                'color': random.random(),
                'weight': random.uniform(0.1, 1.0),
                'variation': random.choice(['linear', 'sinusoidal', 'spherical', 'swirl'])
            }
            self.functions.append(function)
            
        # Normalize weights
        total_weight = sum(f['weight'] for f in self.functions)
        for f in self.functions:
            f['weight'] /= total_weight
            
    def apply_variation(self, x, y, variation_type):
        r = math.sqrt(x*x + y*y)
        theta = math.atan2(y, x)
        
        if variation_type == 'linear':
            return x, y
        elif variation_type == 'sinusoidal':
            return math.sin(x), math.sin(y)
        elif variation_type == 'spherical':
            if r != 0:
                return x/r**2, y/r**2
            return 0, 0
        elif variation_type == 'swirl':
            return x*math.sin(r**2) - y*math.cos(r**2), x*math.cos(r**2) + y*math.sin(r**2)
        
        return x, y  # Default
    
    def generate(self, iterations=5000000, final_iterations=20):
        # Reset histogram
        self.histogram = np.zeros((self.height, self.width, 3), dtype=np.float64)
        
        # Initial point
        x, y = 0, 0
        
        # Skip the first iterations to let the attractor converge
        for _ in range(20):
            # Choose a function based on weights
            r = random.random()
            cumulative_weight = 0
            chosen_f = None
            
            for f in self.functions:
                cumulative_weight += f['weight']
                if r <= cumulative_weight:
                    chosen_f = f
                    break
            
            # Apply affine transform
            new_x = chosen_f['a'] * x + chosen_f['b'] * y + chosen_f['e']
            new_y = chosen_f['c'] * x + chosen_f['d'] * y + chosen_f['f']
            
            # Apply variation
            x, y = self.apply_variation(new_x, new_y, chosen_f['variation'])
        
        # Main iterations
        for i in range(iterations):
            # Choose a function based on weights
            r = random.random()
            cumulative_weight = 0
            chosen_f = None
            
            for f in self.functions:
                cumulative_weight += f['weight']
                if r <= cumulative_weight:
                    chosen_f = f
                    break
            
            # Apply affine transform
            new_x = chosen_f['a'] * x + chosen_f['b'] * y + chosen_f['e']
            new_y = chosen_f['c'] * x + chosen_f['d'] * y + chosen_f['f']
            
            # Apply variation
            x, y = self.apply_variation(new_x, new_y, chosen_f['variation'])
            
            # Map to screen coordinates
            screen_x = int((x + 2) * self.width / 4)
            screen_y = int((y + 2) * self.height / 4)
            
            # Check if point is in bounds
            if 0 <= screen_x < self.width and 0 <= screen_y < self.height:
                # Update histogram with color
                color_idx = int(chosen_f['color'] * (len(self.palette) - 1))
                r, g, b = self.palette[color_idx]
                
                self.histogram[screen_y, screen_x, 0] += r / 255.0
                self.histogram[screen_y, screen_x, 1] += g / 255.0
                self.histogram[screen_y, screen_x, 2] += b / 255.0
        
        # Final rendering passes
        for _ in range(final_iterations):
            self.apply_gamma_correction()
            self.apply_log_density()
        
        # Create Pygame surface
        surface = pygame.Surface((self.width, self.height))
        
        # Normalize histogram
        max_value = np.max(self.histogram)
        if max_value > 0:
            self.histogram = self.histogram / max_value
            
        # Map to surface
        for y in range(self.height):
            for x in range(self.width):
                r = int(min(255, self.histogram[y, x, 0] * 255))
                g = int(min(255, self.histogram[y, x, 1] * 255))
                b = int(min(255, self.histogram[y, x, 2] * 255))
                surface.set_at((x, y), (r, g, b))
                
        return surface
    
    def apply_gamma_correction(self, gamma=2.2):
        # Apply gamma correction to the histogram
        mask = self.histogram > 0
        self.histogram[mask] = self.histogram[mask] ** (1.0 / gamma)
        
    def apply_log_density(self):
        # Apply logarithmic density mapping
        mask = self.histogram > 0
        self.histogram[mask] = np.log(self.histogram[mask] + 1) / np.log(10)

# L-System Fractal Generator
class LSystemGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.axiom = ""
        self.rules = {}
        self.iterations = 4
        self.angle = 25
        self.start_length = 10
        self.scale_factor = 0.5
        self.palette = generate_random_palette()
        self.init_system()
        
    def init_system(self):
        # Choose one of several predefined L-systems
        systems = [
            {  # Koch curve
                'axiom': 'F',
                'rules': {'F': 'F+F-F-F+F'},
                'angle': 90,
                'iterations': 4
            },
            {  # Sierpinski triangle
                'axiom': 'F-G-G',
                'rules': {'F': 'F-G+F+G-F', 'G': 'GG'},
                'angle': 120,
                'iterations': 5
            },
            {  # Dragon curve
                'axiom': 'FX',
                'rules': {'X': 'X+YF+', 'Y': '-FX-Y'},
                'angle': 90,
                'iterations': 10
            },
            {  # Fractal plant
                'axiom': 'X',
                'rules': {'X': 'F-[[X]+X]+F[+FX]-X', 'F': 'FF'},
                'angle': 25,
                'iterations': 5
            }
        ]
        
        system = random.choice(systems)
        self.axiom = system['axiom']
        self.rules = system['rules']
        self.angle = system['angle']
        self.iterations = system['iterations']
        
    def generate_path(self):
        # Apply rules for specified number of iterations
        path = self.axiom
        for _ in range(self.iterations):
            new_path = ""
            for char in path:
                if char in self.rules:
                    new_path += self.rules[char]
                else:
                    new_path += char
            path = new_path
            
        return path
        
    def generate(self):
        path = self.generate_path()
        
        # Create surface
        surface = pygame.Surface((self.width, self.height))
        surface.fill((0, 0, 0))
        
        # Initial position and orientation
        x, y = self.width // 2, self.height * 0.8
        angle = -90  # Start facing up
        stack = []
        length = self.start_length
        
        # Choose a line color
        line_color = random.choice(self.palette)
        
        # Estimate bounds to scale properly
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')
        
        test_x, test_y = x, y
        test_angle = angle
        
        for char in path:
            if char == 'F' or char == 'G':  # Move forward
                test_x += length * math.cos(math.radians(test_angle))
                test_y += length * math.sin(math.radians(test_angle))
                min_x = min(min_x, test_x)
                min_y = min(min_y, test_y)
                max_x = max(max_x, test_x)
                max_y = max(max_y, test_y)
            elif char == '+':  # Turn right
                test_angle += self.angle
            elif char == '-':  # Turn left
                test_angle -= self.angle
            elif char == '[':  # Save state
                stack.append((test_x, test_y, test_angle))
            elif char == ']':  # Restore state
                test_x, test_y, test_angle = stack.pop()
        
        # Calculate scaling and translation
        if min_x < float('inf') and max_x > float('-inf'):
            scale = min(
                self.width * 0.9 / (max_x - min_x) if max_x > min_x else 1,
                self.height * 0.9 / (max_y - min_y) if max_y > min_y else 1
            )
            
            # Start position
            x = self.width // 2 - (min_x + max_x) / 2 * scale
            y = self.height * 0.9 - min_y * scale
            length *= scale
        
        # Actually draw the L-system
        stack = []
        for char in path:
            if char == 'F' or char == 'G':  # Move forward
                new_x = x + length * math.cos(math.radians(angle))
                new_y = y + length * math.sin(math.radians(angle))
                pygame.draw.line(surface, line_color, (x, y), (new_x, new_y), 1)
                x, y = new_x, new_y
            elif char == '+':  # Turn right
                angle += self.angle
            elif char == '-':  # Turn left
                angle -= self.angle
            elif char == '[':  # Save state
                stack.append((x, y, angle, length))
            elif char == ']':  # Restore state
                x, y, angle, length = stack.pop()
            elif char == '(':  # Decrease line width (not implemented yet)
                pass
            elif char == ')':  # Increase line width (not implemented yet)
                pass
        
        return surface

if __name__ == "__main__":
    app = GenerativeArtStudio()
    app.run()
