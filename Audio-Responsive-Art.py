import pygame
import math
import random
import sys
from pygame import gfxdraw

# Initialize pygame
pygame.init()
width, height = 1000, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Geometric Harmony")
clock = pygame.time.Clock()

# Colors
background = (10, 10, 15)
colors = [
    (52, 152, 219, 0),  # Blue
    (231, 76, 60, 0),   # Red
    (46, 204, 113, 0),  # Green
    (241, 196, 15, 0),  # Yellow
    (155, 89, 182, 0)   # Purple
]

# Particle system
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2, 6)
        self.color = random.choice(colors)[:3]
        self.alpha = random.randint(30, 100)
        self.speed = random.uniform(0.2, 1.5)
        self.angle = random.uniform(0, 2 * math.pi)
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.alpha -= 0.5
        return self.alpha > 0
        
    def draw(self, surface):
        if self.alpha > 0:
            gfxdraw.filled_circle(surface, int(self.x), int(self.y), self.size, 
                                 (self.color[0], self.color[1], self.color[2], int(self.alpha)))

# Geometric elements
class Circle:
    def __init__(self, x, y, max_radius, color, phase=0):
        self.x = x
        self.y = y
        self.max_radius = max_radius
        self.color = color
        self.phase = phase
        self.progress = 0
        self.growing = True
        self.alive = True
        
    def update(self, t):
        if self.growing:
            self.progress += 0.01
            if self.progress >= 1:
                self.growing = False
        else:
            self.progress -= 0.01
            if self.progress <= 0:
                self.alive = False
                
    def draw(self, surface, t):
        radius = self.max_radius * self.progress
        thickness = int(3 + 2 * math.sin(t * 2 + self.phase))
        if thickness < 1: thickness = 1
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(radius), thickness)

class Line:
    def __init__(self, start_x, start_y, end_x, end_y, color, phase=0):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.color = color
        self.phase = phase
        self.progress = 0
        self.growing = True
        self.alive = True
        
    def update(self, t):
        if self.growing:
            self.progress += 0.02
            if self.progress >= 1:
                self.growing = False
        else:
            self.progress -= 0.02
            if self.progress <= 0:
                self.alive = False
                
    def draw(self, surface, t):
        current_end_x = self.start_x + (self.end_x - self.start_x) * self.progress
        current_end_y = self.start_y + (self.end_y - self.start_y) * self.progress
        thickness = int(2 + math.sin(t * 3 + self.phase))
        if thickness < 1: thickness = 1
        pygame.draw.line(surface, self.color, (self.start_x, self.start_y), 
                         (current_end_x, current_end_y), thickness)

class Square:
    def __init__(self, center_x, center_y, max_size, color, phase=0):
        self.center_x = center_x
        self.center_y = center_y
        self.max_size = max_size
        self.color = color
        self.phase = phase
        self.progress = 0
        self.growing = True
        self.alive = True
        self.rotation = 0
        
    def update(self, t):
        if self.growing:
            self.progress += 0.01
            if self.progress >= 1:
                self.growing = False
        else:
            self.progress -= 0.01
            if self.progress <= 0:
                self.alive = False
        self.rotation += 0.01
                
    def draw(self, surface, t):
        size = self.max_size * self.progress
        thickness = int(2 + math.sin(t * 2.5 + self.phase))
        if thickness < 1: thickness = 1
        
        # Calculate rotated points
        points = []
        for i in range(4):
            angle = self.rotation + i * math.pi / 2
            x = self.center_x + size * math.cos(angle)
            y = self.center_y + size * math.sin(angle)
            points.append((int(x), int(y)))
        
        pygame.draw.polygon(surface, self.color, points, thickness)

class DragonCurve:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.iterations = 12
        self.angle = 0
        self.progress = 0
        self.points = []
        self.generate_dragon_curve()
        self.alive = True
        
    def generate_dragon_curve(self):
        # Generate the dragon curve sequence
        sequence = [1]
        for i in range(self.iterations):
            new_sequence = sequence.copy()
            new_sequence.append(1)
            for j in range(len(sequence) - 1, -1, -1):
                new_sequence.append(1 - sequence[j])
            sequence = new_sequence
            
        # Convert sequence to points
        x, y = 0, 0
        direction = 0  # 0: right, 1: up, 2: left, 3: down
        self.points = [(x, y)]
        
        for turn in sequence:
            if turn == 1:  # Turn right
                direction = (direction + 1) % 4
            else:  # Turn left
                direction = (direction - 1) % 4
                
            if direction == 0:
                x += 1
            elif direction == 1:
                y -= 1
            elif direction == 2:
                x -= 1
            else:
                y += 1
                
            self.points.append((x, y))
            
    def update(self, t):
        self.angle += 0.005
        if self.progress < 1:
            self.progress += 0.002
        
    def draw(self, surface, t):
        # Scale and position the curve
        scale = self.size * 0.05
        visible_points = int(len(self.points) * self.progress)
        
        for i in range(1, visible_points):
            # Get original points
            x1, y1 = self.points[i-1]
            x2, y2 = self.points[i]
            
            # Rotate points
            cos_a = math.cos(self.angle)
            sin_a = math.sin(self.angle)
            
            rx1 = x1 * cos_a - y1 * sin_a
            ry1 = x1 * sin_a + y1 * cos_a
            
            rx2 = x2 * cos_a - y2 * sin_a
            ry2 = x2 * sin_a + y2 * cos_a
            
            # Scale and position
            px1 = int(self.x + rx1 * scale)
            py1 = int(self.y + ry1 * scale)
            px2 = int(self.x + rx2 * scale)
            py2 = int(self.y + ry2 * scale)
            
            # Determine color and alpha based on position in sequence
            progress_factor = i / len(self.points)
            alpha = int(255 * (1 - progress_factor))
            color = list(self.color)
            if len(color) == 3:
                color.append(alpha)
            else:
                color[3] = alpha
                
            # Draw line segment
            pygame.draw.line(surface, color, (px1, py1), (px2, py2), 2)

# Main animation loop
def main():
    # Create surfaces for blending
    main_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    particle_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Create geometric elements
    circles = []
    squares = []
    lines = []
    particles = []
    dragon = None
    
    t = 0
    running = True
    spawn_timer = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # Clear surfaces
        main_surface.fill((0, 0, 0, 0))
        particle_surface.fill((0, 0, 0, 0))
        screen.fill(background)
        
        # Update time
        t += 0.01
        spawn_timer += 1
        
        # Spawn new elements
        if spawn_timer >= 30:
            spawn_timer = 0
            
            # Random element type
            element_type = random.choice(['circle', 'square', 'line', 'dragon'])
            color = random.choice(colors)[:3]
            
            if element_type == 'circle':
                x = random.randint(100, width - 100)
                y = random.randint(100, height - 100)
                radius = random.randint(50, 150)
                circles.append(Circle(x, y, radius, color, random.random() * math.pi))
                
            elif element_type == 'square':
                x = random.randint(100, width - 100)
                y = random.randint(100, height - 100)
                size = random.randint(40, 120)
                squares.append(Square(x, y, size, color, random.random() * math.pi))
                
            elif element_type == 'line':
                x1 = random.randint(100, width - 100)
                y1 = random.randint(100, height - 100)
                angle = random.random() * 2 * math.pi
                length = random.randint(100, 300)
                x2 = x1 + length * math.cos(angle)
                y2 = y1 + length * math.sin(angle)
                lines.append(Line(x1, y1, x2, y2, color, random.random() * math.pi))
                
            elif element_type == 'dragon' and dragon is None:
                dragon = DragonCurve(width//2, height//2, 200, color)
        
        # Add particles occasionally
        if random.random() < 0.3:
            for _ in range(5):
                particles.append(Particle(
                    random.randint(0, width),
                    random.randint(0, height)
                ))
        
        # Update and draw particles
        particles = [p for p in particles if p.update()]
        for particle in particles:
            particle.draw(particle_surface)
        
        # Update and draw circles
        for circle in circles[:]:
            circle.update(t)
            if not circle.alive:
                circles.remove(circle)
            else:
                circle.draw(main_surface, t)
        
        # Update and draw squares
        for square in squares[:]:
            square.update(t)
            if not square.alive:
                squares.remove(square)
            else:
                square.draw(main_surface, t)
        
        # Update and draw lines
        for line in lines[:]:
            line.update(t)
            if not line.alive:
                lines.remove(line)
            else:
                line.draw(main_surface, t)
        
        # Update and draw dragon curve
        if dragon:
            dragon.update(t)
            dragon.draw(main_surface, t)
        
        # Draw text that fades in and out
        if int(t * 10) % 300 == 0:
            font = pygame.font.SysFont('Arial', 30)
            text = font.render("Geometric Harmony", True, (255, 255, 255, int(128 + 127 * math.sin(t))))
            text_rect = text.get_rect(center=(width//2, height//2))
            main_surface.blit(text, text_rect)
        
        # Blend surfaces and display
        screen.blit(particle_surface, (0, 0))
        screen.blit(main_surface, (0, 0))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()