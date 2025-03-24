import pygame
import math
import random
import colorsys
import numpy as np

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sleek Particle Symphony")

# Colors
BACKGROUND = (10, 10, 15)
WHITE = (255, 255, 255)

class ParticleSystem:
    def __init__(self, num_particles=800):
        self.particles = []
        for _ in range(num_particles):
            self.particles.append(self.create_particle())
        self.mode = 0
        self.time = 0
        self.modes = ["Orbital", "Waves", "Geometric", "Swarm"]
        self.color_scheme = 0
        self.color_schemes = ["Monochrome", "Gradient", "Rainbow"]
        self.base_hue = random.random()
        self.mouse_pos = (WIDTH/2, HEIGHT/2)
        self.mouse_influence = 0.0
        self.pulse_intensity = 0.0
        
    def create_particle(self):
        return {
            'pos': [random.uniform(0, WIDTH), random.uniform(0, HEIGHT)],
            'vel': [random.uniform(-1, 1), random.uniform(-1, 1)],
            'radius': random.uniform(1.5, 3.5),
            'hue': random.random(),
            'alpha': random.uniform(0.5, 1.0),
            'phase': random.uniform(0, math.pi * 2)
        }
    
    def get_color(self, particle):
        # Base particle hue
        h = particle['hue']
        
        if self.color_scheme == 0:  # Monochrome
            h = self.base_hue
            s = 0.1 + 0.6 * self.pulse_intensity
            v = 0.8 + 0.2 * self.pulse_intensity
        elif self.color_scheme == 1:  # Gradient
            # Gradient based on position
            h = (self.base_hue + particle['pos'][0] / WIDTH) % 1.0
            s = 0.7 + 0.3 * self.pulse_intensity
            v = 0.8 + 0.2 * self.pulse_intensity
        else:  # Rainbow
            # Cycle hues over time
            h = (h + self.time * 0.001) % 1.0
            s = 0.7
            v = 0.9
        
        # Convert to RGB
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
        
        # Apply alpha
        alpha = int(255 * particle['alpha'] * (0.7 + 0.3 * self.pulse_intensity))
        
        return (r, g, b, alpha)
    
    def update(self):
        self.time += 1
        self.pulse_intensity *= 0.95  # Decay pulse
        
        # Update each particle based on current mode
        for p in self.particles:
            if self.mode == 0:  # Orbital
                self.update_orbital(p)
            elif self.mode == 1:  # Waves
                self.update_waves(p)
            elif self.mode == 2:  # Geometric
                self.update_geometric(p)
            elif self.mode == 3:  # Swarm
                self.update_swarm(p)
    
    def update_orbital(self, p):
        # Calculate center point (either mouse or screen center)
        center_x = self.mouse_pos[0] if self.mouse_influence > 0.5 else WIDTH/2
        center_y = self.mouse_pos[1] if self.mouse_influence > 0.5 else HEIGHT/2
        
        # Vector from particle to center
        dx = center_x - p['pos'][0]
        dy = center_y - p['pos'][1]
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < 1:
            dist = 1
            
        # Orbital velocity
        angle = math.atan2(dy, dx)
        orbital_speed = 2 + self.pulse_intensity * 3
        
        # Apply orbital force (perpendicular to center vector)
        p['vel'][0] += -math.sin(angle) * orbital_speed / (dist ** 0.5)
        p['vel'][1] += math.cos(angle) * orbital_speed / (dist ** 0.5)
        
        # Apply slight attraction to center
        p['vel'][0] += dx * 0.0003
        p['vel'][1] += dy * 0.0003
        
        # Update position
        p['pos'][0] += p['vel'][0]
        p['pos'][1] += p['vel'][1]
        
        # Dampen velocity
        p['vel'][0] *= 0.99
        p['vel'][1] *= 0.99
        
        # Keep particles on screen with smooth wrapping
        margin = 50
        if p['pos'][0] < -margin: p['pos'][0] = WIDTH + margin
        if p['pos'][0] > WIDTH + margin: p['pos'][0] = -margin
        if p['pos'][1] < -margin: p['pos'][1] = HEIGHT + margin
        if p['pos'][1] > HEIGHT + margin: p['pos'][1] = -margin
    
    def update_waves(self, p):
        # Wave parameters
        wave_speed = 0.05
        amplitude = 20 + self.pulse_intensity * 30
        frequency = 0.005
        
        # Calculate wave offset based on position and time
        offset_x = math.sin(p['pos'][1] * frequency + self.time * wave_speed) * amplitude
        offset_y = math.sin(p['pos'][0] * frequency + self.time * wave_speed) * amplitude
        
        # Target position: grid with wave offsets
        grid_size = 40
        target_x = (int(p['pos'][0] / grid_size) * grid_size) + offset_x
        target_y = (int(p['pos'][1] / grid_size) * grid_size) + offset_y
        
        # Move towards target
        p['vel'][0] += (target_x - p['pos'][0]) * 0.05
        p['vel'][1] += (target_y - p['pos'][1]) * 0.05
        
        # Mouse influence
        if self.mouse_influence > 0.5:
            dx = self.mouse_pos[0] - p['pos'][0]
            dy = self.mouse_pos[1] - p['pos'][1]
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 200:
                p['vel'][0] += dx * 0.001 * (1 - dist/200)
                p['vel'][1] += dy * 0.001 * (1 - dist/200)
        
        # Update position
        p['pos'][0] += p['vel'][0]
        p['pos'][1] += p['vel'][1]
        
        # Dampen velocity
        p['vel'][0] *= 0.95
        p['vel'][1] *= 0.95
        
        # Keep particles on screen
        if p['pos'][0] < 0: p['pos'][0] = 0
        if p['pos'][0] > WIDTH: p['pos'][0] = WIDTH
        if p['pos'][1] < 0: p['pos'][1] = 0
        if p['pos'][1] > HEIGHT: p['pos'][1] = HEIGHT
    
    def update_geometric(self, p):
        # Time-based parameters
        time_factor = self.time * 0.001
        points = 5  # Number of points in shape
        
        # Calculate distances to each point of shape
        distances = []
        for i in range(points):
            angle = i * (2 * math.pi / points) + time_factor
            point_x = WIDTH/2 + math.cos(angle) * 300
            point_y = HEIGHT/2 + math.sin(angle) * 300
            
            dx = point_x - p['pos'][0]
            dy = point_y - p['pos'][1]
            dist = math.sqrt(dx*dx + dy*dy)
            distances.append((dist, dx, dy))
        
        # Find closest point
        closest = min(distances, key=lambda x: x[0])
        dist, dx, dy = closest
        
        # Move towards closest point
        attraction = 0.01 + self.pulse_intensity * 0.02
        p['vel'][0] += dx * attraction
        p['vel'][1] += dy * attraction
        
        # Apply repulsion from other particles nearby
        for other in random.sample(self.particles, min(5, len(self.particles))):
            if other != p:
                dx = p['pos'][0] - other['pos'][0]
                dy = p['pos'][1] - other['pos'][1]
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < 30:
                    p['vel'][0] += dx * 0.01 * (1 - dist/30)
                    p['vel'][1] += dy * 0.01 * (1 - dist/30)
        
        # Update position
        p['pos'][0] += p['vel'][0]
        p['pos'][1] += p['vel'][1]
        
        # Dampen velocity
        p['vel'][0] *= 0.95
        p['vel'][1] *= 0.95
    
    def update_swarm(self, p):
        # Swarm behavior parameters
        separation = 0.02
        alignment = 0.01
        cohesion = 0.005
        
        # Get nearby particles
        neighbors = []
        for other in random.sample(self.particles, min(20, len(self.particles))):
            if other != p:
                dx = other['pos'][0] - p['pos'][0]
                dy = other['pos'][1] - p['pos'][1]
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < 100:
                    neighbors.append((other, dist, dx, dy))
        
        if neighbors:
            # Separation: avoid crowding neighbors
            sep_x, sep_y = 0, 0
            for other, dist, dx, dy in neighbors:
                if dist < 50:
                    factor = 1 - dist/50
                    sep_x -= dx * factor
                    sep_y -= dy * factor
            
            # Alignment: steer towards average heading of neighbors
            avg_vel_x, avg_vel_y = 0, 0
            for other, _, _, _ in neighbors:
                avg_vel_x += other['vel'][0]
                avg_vel_y += other['vel'][1]
            avg_vel_x /= len(neighbors)
            avg_vel_y /= len(neighbors)
            
            # Cohesion: steer towards center of neighbors
            avg_pos_x, avg_pos_y = 0, 0
            for other, _, _, _ in neighbors:
                avg_pos_x += other['pos'][0]
                avg_pos_y += other['pos'][1]
            avg_pos_x /= len(neighbors)
            avg_pos_y /= len(neighbors)
            
            # Apply forces
            p['vel'][0] += sep_x * separation + (avg_vel_x - p['vel'][0]) * alignment + (avg_pos_x - p['pos'][0]) * cohesion
            p['vel'][1] += sep_y * separation + (avg_vel_y - p['vel'][1]) * alignment + (avg_pos_y - p['pos'][1]) * cohesion
        
        # Mouse influence as attractor/repulsor
        if self.mouse_influence > 0.1:
            dx = self.mouse_pos[0] - p['pos'][0]
            dy = self.mouse_pos[1] - p['pos'][1]
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 200:
                factor = self.mouse_influence * 0.02 * (1 - dist/200)
                p['vel'][0] += dx * factor
                p['vel'][1] += dy * factor
        
        # Apply speed limit
        speed = math.sqrt(p['vel'][0]**2 + p['vel'][1]**2)
        max_speed = 3 + self.pulse_intensity * 2
        if speed > max_speed:
            p['vel'][0] = (p['vel'][0] / speed) * max_speed
            p['vel'][1] = (p['vel'][1] / speed) * max_speed
        
        # Update position
        p['pos'][0] += p['vel'][0]
        p['pos'][1] += p['vel'][1]
        
        # Wrap around screen edges smoothly
        margin = 50
        if p['pos'][0] < -margin: p['pos'][0] = WIDTH + margin
        if p['pos'][0] > WIDTH + margin: p['pos'][0] = -margin
        if p['pos'][1] < -margin: p['pos'][1] = HEIGHT + margin
        if p['pos'][1] > HEIGHT + margin: p['pos'][1] = -margin
    
    def draw(self, surface):
        # Clear screen with slight fade for trail effect
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((BACKGROUND[0], BACKGROUND[1], BACKGROUND[2], 20))
        surface.blit(overlay, (0, 0))
        
        # Draw connections between particles in some modes
        if self.mode in [2, 3]:  # Geometric and Swarm modes
            self.draw_connections(surface)
        
        # Draw particles
        for p in self.particles:
            # Get particle color
            color = self.get_color(p)
            
            # Calculate size with pulse effect
            radius = p['radius'] * (1 + self.pulse_intensity * 0.5)
            
            # Draw with anti-aliasing
            pygame.draw.circle(surface, color, (int(p['pos'][0]), int(p['pos'][1])), int(radius))
    
    def draw_connections(self, surface):
        # Draw lines between nearby particles
        max_dist = 100
        
        # Use a subset of particles for better performance
        subset = random.sample(self.particles, min(200, len(self.particles)))
        
        for i, p1 in enumerate(subset):
            for p2 in subset[i+1:]:
                dx = p1['pos'][0] - p2['pos'][0]
                dy = p1['pos'][1] - p2['pos'][1]
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < max_dist:
                    # Calculate alpha based on distance
                    alpha = int(255 * (1 - dist/max_dist) * 0.5)
                    
                    # Get average color
                    color1 = self.get_color(p1)
                    color2 = self.get_color(p2)
                    avg_color = (
                        (color1[0] + color2[0]) // 2,
                        (color1[1] + color2[1]) // 2,
                        (color1[2] + color2[2]) // 2,
                        alpha
                    )
                    
                    # Draw line
                    pygame.draw.line(
                        surface, 
                        avg_color, 
                        (int(p1['pos'][0]), int(p1['pos'][1])),
                        (int(p2['pos'][0]), int(p2['pos'][1])),
                        1
                    )
    
    def trigger_pulse(self):
        self.pulse_intensity = 1.0
        
    def change_mode(self):
        self.mode = (self.mode + 1) % len(self.modes)
        
    def change_color_scheme(self):
        self.color_scheme = (self.color_scheme + 1) % len(self.color_schemes)
        self.base_hue = random.random()  # New base hue when changing schemes

def main():
    # Initialize the screen
    clock = pygame.time.Clock()
    
    # Create particle system
    particles = ParticleSystem(800)
    
    # Font setup
    font = pygame.font.SysFont('Arial', 16)
    
    # UI fade timer
    ui_visible = True
    ui_timer = 0
    
    # Main loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    particles.change_mode()
                    particles.trigger_pulse()
                elif event.key == pygame.K_c:
                    particles.change_color_scheme()
                    particles.trigger_pulse()
                elif event.key == pygame.K_p:
                    particles.trigger_pulse()
                elif event.key == pygame.K_h:
                    ui_visible = not ui_visible
                    ui_timer = 0
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                particles.trigger_pulse()
                
        # Get mouse state
        mouse_pos = pygame.mouse.get_pos()
        particles.mouse_pos = mouse_pos
        
        # Set mouse influence based on mouse button state
        if pygame.mouse.get_pressed()[0]:  # Left button
            particles.mouse_influence = 1.0
        elif pygame.mouse.get_pressed()[2]:  # Right button
            particles.mouse_influence = -1.0
        else:
            # Gradually decrease influence
            particles.mouse_influence *= 0.95
        
        # Update particles
        particles.update()
        
        # Draw everything
        screen.fill(BACKGROUND)
        particles.draw(screen)
        
        # Draw UI if visible
        if ui_visible or ui_timer < 180:  # Show UI for 3 seconds after last interaction
            ui_timer += 1
            
            # Calculate UI opacity
            opacity = 255
            if not ui_visible and ui_timer > 60:
                opacity = max(0, 255 - (ui_timer - 60) * 2)
            
            # Draw mode and controls info
            mode_text = f"Mode: {particles.modes[particles.mode]}"
            color_text = f"Color: {particles.color_schemes[particles.color_scheme]}"
            controls_text = "SPACE: Change Mode | C: Change Colors | P: Pulse | H: Hide UI"
            mouse_text = "Mouse: Left click to attract, Right click to repel"
            
            # Render text with shadow for better visibility
            def draw_text_with_shadow(text, pos, color, shadow_color=(20, 20, 20, opacity)):
                # Shadow
                shadow_surf = font.render(text, True, shadow_color)
                screen.blit(shadow_surf, (pos[0]+1, pos[1]+1))
                # Text
                text_surf = font.render(text, True, (*color, opacity))
                screen.blit(text_surf, pos)
            
            draw_text_with_shadow(mode_text, (10, 10), WHITE)
            draw_text_with_shadow(color_text, (10, 30), WHITE)
            draw_text_with_shadow(controls_text, (10, HEIGHT - 40), WHITE)
            draw_text_with_shadow(mouse_text, (10, HEIGHT - 20), WHITE)
            
            # Show FPS
            fps_text = f"FPS: {int(clock.get_fps())}"
            draw_text_with_shadow(fps_text, (WIDTH - 80, 10), WHITE)
        
        # Update display
        pygame.display.flip()
        
        # Cap at 60 FPS
        clock.tick(60)
    
    pygame.quit()

# Create smooth gradient background
def create_gradient_background(width, height, color1, color2):
    surface = pygame.Surface((width, height))
    for y in range(height):
        # Calculate color for this row
        r = int(color1[0] * (1 - y/height) + color2[0] * (y/height))
        g = int(color1[1] * (1 - y/height) + color2[1] * (y/height))
        b = int(color1[2] * (1 - y/height) + color2[2] * (y/height))
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
    return surface

# Helper function to create smooth curves
def bezier(p0, p1, p2, p3, t):
    return (
        (1-t)**3 * p0[0] + 3*(1-t)**2*t * p1[0] + 3*(1-t)*t**2 * p2[0] + t**3 * p3[0],
        (1-t)**3 * p0[1] + 3*(1-t)**2*t * p1[1] + 3*(1-t)*t**2 * p2[1] + t**3 * p3[1]
    )

# Entry point
if __name__ == "__main__":
    main()