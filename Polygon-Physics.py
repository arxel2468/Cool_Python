import pygame
import math
import random
import numpy as np
from pygame import gfxdraw

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # For sound effects

# Constants
WIDTH = 800
HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)

# Default Physics constants
DEFAULT_GRAVITY = 981.0  # pixels/second^2
DEFAULT_ROTATION_SPEED = 1.0  # radians/second
DEFAULT_ELASTICITY = 0.7
DEFAULT_FRICTION = 0.99
DEFAULT_SIDES = 6  # Hexagon by default

# Current physics settings
gravity = DEFAULT_GRAVITY
rotation_speed = DEFAULT_ROTATION_SPEED
elasticity = DEFAULT_ELASTICITY
friction = DEFAULT_FRICTION
polygon_sides = DEFAULT_SIDES
auto_rotate = True
shape_radius = 150
show_trails = False
gravity_point_active = False
gravity_point_pos = (WIDTH/2, HEIGHT/2)
gravity_point_strength = 500
enable_particle_effects = True

# Colors for the balls
BALL_COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE, CYAN, MAGENTA, GOLD, SILVER]

# Game state
score = 0
game_mode = False
time_elapsed = 0
target_position = (0, 0)
target_active = False
target_timer = 0
target_timeout = 5  # seconds

# Themes
themes = ["Default", "Neon", "Space", "Underwater", "Fire"]
current_theme = 0

# Particle effect class
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(1, 3)
        self.life = random.uniform(0.2, 0.8)
        self.vel_x = random.uniform(-50, 50)
        self.vel_y = random.uniform(-50, 50)
        self.alpha = 255
        
    def update(self, dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.life -= dt
        self.alpha = max(0, int(255 * (self.life / 0.8)))
        return self.life > 0
        
    def draw(self, screen):
        if self.alpha > 0:
            color_with_alpha = (*self.color[:3], self.alpha)
            s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, color_with_alpha, (self.size, self.size), self.size)
            screen.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class Trail:
    def __init__(self, max_points=20):
        self.points = []
        self.max_points = max_points
        
    def add_point(self, pos):
        self.points.append(pos)
        if len(self.points) > self.max_points:
            self.points.pop(0)
            
    def draw(self, screen, color):
        if len(self.points) > 1:
            for i in range(1, len(self.points)):
                alpha = int(255 * (i / len(self.points)))
                pygame.draw.line(screen, (*color[:3], alpha), 
                                self.points[i-1], self.points[i], 
                                max(1, int(i / 2)))

class Ball:
    def __init__(self, x, y, radius, color=RED):
        self.x = x
        self.y = y
        self.radius = radius
        self.vel_x = random.uniform(-50, 50)
        self.vel_y = random.uniform(-50, 50)
        self.is_colliding = False
        self.color = color
        self.mass = radius**2  # Mass proportional to area
        self.trail = Trail()
        self.collision_time = 0
        self.glow = 0
        self.particles = []
        
    def update(self, dt):
        old_x, old_y = self.x, self.y
        
        # Update position based on velocity
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
        # Apply constant downward gravity (no rotation)
        self.vel_y += gravity * dt
        
        # Apply gravity point if active
        if gravity_point_active:
            dx = gravity_point_pos[0] - self.x
            dy = gravity_point_pos[1] - self.y
            distance = max(10, math.sqrt(dx*dx + dy*dy))
            force = gravity_point_strength / (distance * self.mass)
            self.vel_x += dx * force * dt
            self.vel_y += dy * force * dt
        
        # Apply friction only when in contact with walls
        if self.is_colliding:
            self.vel_x *= friction
            self.vel_y *= friction
            self.collision_time = 0.1  # Set collision glow duration
            
            # Add collision particles
            if enable_particle_effects:
                for _ in range(5):
                    self.particles.append(Particle(self.x, self.y, self.color))
                
        # Update collision glow
        if self.collision_time > 0:
            self.collision_time -= dt
            self.glow = min(255, int(255 * (self.collision_time / 0.1)))
        else:
            self.glow = 0
            
        # Update particles
        if enable_particle_effects:
            self.particles = [p for p in self.particles if p.update(dt)]
        
        # Add point to trail
        if show_trails:
            self.trail.add_point((int(self.x), int(self.y)))
            
        self.is_colliding = False  # Reset collision flag

    def check_target_collision(self):
        if target_active:
            dx = self.x - target_position[0]
            dy = self.y - target_position[1]
            distance = math.sqrt(dx*dx + dy*dy)
            if distance < self.radius + 20:  # Target radius is 20
                return True
        return False
        
    def draw(self, screen):
        # Draw trail if enabled
        if show_trails:
            self.trail.draw(screen, self.color)
            
        # Draw particles
        if enable_particle_effects:
            for particle in self.particles:
                particle.draw(screen)
        
        # Draw ball with glow effect if recently collided
        if self.glow > 0:
            # Draw outer glow
            s = pygame.Surface((self.radius*2 + 10, self.radius*2 + 10), pygame.SRCALPHA)
            glow_color = (*self.color[:3], self.glow)
            pygame.draw.circle(s, glow_color, (self.radius + 5, self.radius + 5), self.radius + 5)
            screen.blit(s, (int(self.x - self.radius - 5), int(self.y - self.radius - 5)))
            
        # Draw the ball
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw a shading effect for 3D look
        highlight = (min(255, self.color[0] + 50), min(255, self.color[1] + 50), min(255, self.color[2] + 50))
        pygame.draw.circle(screen, highlight, (int(self.x - self.radius/3), int(self.y - self.radius/3)), self.radius/2)

class Polygon:
    def __init__(self, center_x, center_y, radius, sides):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.sides = sides
        self.angle = 0
        self.vertices = self.calculate_vertices()
        self.glow_amount = 0
        self.edge_colors = [WHITE] * sides  # Initialize with white edges
        
    def calculate_vertices(self):
        vertices = []
        for i in range(self.sides):
            angle = self.angle + i * (2 * math.pi / self.sides)
            x = self.center_x + self.radius * math.cos(angle)
            y = self.center_y + self.radius * math.sin(angle)
            vertices.append((x, y))
        return vertices
    
    def update(self, dt):
        if auto_rotate:
            self.angle += rotation_speed * dt
        self.vertices = self.calculate_vertices()
        
        # Fade edge colors back to white
        for i in range(self.sides):
            r, g, b = self.edge_colors[i]
            self.edge_colors[i] = (
                min(255, r + 5),
                min(255, g + 5),
                min(255, b + 5)
            )
        
        # Decrease glow over time
        self.glow_amount = max(0, self.glow_amount - 200 * dt)
        
    def check_collision(self, ball):
        # Check collision with each edge of the polygon
        for i in range(self.sides):
            v1 = self.vertices[i]
            v2 = self.vertices[(i + 1) % self.sides]
            
            # Calculate normal vector to the edge
            edge_x = v2[0] - v1[0]
            edge_y = v2[1] - v1[1]
            normal_x = -edge_y
            normal_y = edge_x
            length = math.sqrt(normal_x**2 + normal_y**2)
            normal_x /= length
            normal_y /= length
            
            # Calculate distance from ball to edge
            dx = ball.x - v1[0]
            dy = ball.y - v1[1]
            distance = abs(dx * normal_x + dy * normal_y)
            
            # Check if the ball is near the line segment
            edge_length = math.sqrt(edge_x**2 + edge_y**2)
            proj = (dx * edge_x + dy * edge_y) / edge_length
            
            # Use a more robust check for line segment collision
            closest_dist = distance
            closest_x = v1[0] + proj * (edge_x / edge_length)
            closest_y = v1[1] + proj * (edge_y / edge_length)
            
            if 0 <= proj <= edge_length:
                # Ball is closest to a point on the line segment
                pass
            else:
                # Ball is closest to an endpoint
                endpoint_dist1 = math.sqrt((ball.x - v1[0])**2 + (ball.y - v1[1])**2)
                endpoint_dist2 = math.sqrt((ball.x - v2[0])**2 + (ball.y - v2[1])**2)
                
                if endpoint_dist1 <= endpoint_dist2:
                    closest_x, closest_y = v1
                    closest_dist = endpoint_dist1
                else:
                    closest_x, closest_y = v2
                    closest_dist = endpoint_dist2
                
                # Recalculate normal for endpoint collision
                if closest_dist > 0:
                    normal_x = (ball.x - closest_x) / closest_dist
                    normal_y = (ball.y - closest_y) / closest_dist
            
            if closest_dist < ball.radius:
                ball.is_colliding = True
                
                # Set edge color based on ball color (but a bit dimmer)
                self.edge_colors[i] = (ball.color[0]//2, ball.color[1]//2, ball.color[2]//2)
                
                # Make the polygon glow
                self.glow_amount = 100
                
                # Project velocity onto normal
                dot_product = (ball.vel_x * normal_x + ball.vel_y * normal_y)
                
                # Only bounce if moving towards the wall
                if dot_product < 0:
                    # Update ball velocity with bounce using elasticity
                    ball.vel_x -= (1 + elasticity) * dot_product * normal_x
                    ball.vel_y -= (1 + elasticity) * dot_product * normal_y
                
                # Move ball outside the wall
                overlap = ball.radius - closest_dist
                ball.x += overlap * normal_x
                ball.y += overlap * normal_y
                
                # Apply global effects
                global score
                if game_mode:
                    score += 1

    def draw(self, screen):
        # Draw glow effect
        if self.glow_amount > 0:
            glow_vertices = []
            for x, y in self.vertices:
                dx = x - self.center_x
                dy = y - self.center_y
                distance = math.sqrt(dx*dx + dy*dy)
                if distance > 0:
                    glow_x = self.center_x + dx / distance * (distance + 10)
                    glow_y = self.center_y + dy / distance * (distance + 10)
                    glow_vertices.append((glow_x, glow_y))
                else:
                    glow_vertices.append((x, y))
                    
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            glow_color = (255, 255, 255, int(self.glow_amount))
            pygame.draw.polygon(s, glow_color, glow_vertices)
            screen.blit(s, (0, 0))
        
        # Draw polygon edges with their respective colors
        for i in range(self.sides):
            v1 = self.vertices[i]
            v2 = self.vertices[(i + 1) % self.sides]
            pygame.draw.line(screen, self.edge_colors[i], v1, v2, 2)

def apply_theme(theme_name):
    global BALL_COLORS, gravity
    
    if theme_name == "Default":
        BALL_COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE, CYAN, MAGENTA, GOLD, SILVER]
        gravity = DEFAULT_GRAVITY
        screen.fill(BLACK)
    elif theme_name == "Neon":
        # Bright, vibrant colors
        BALL_COLORS = [(255, 0, 128), (0, 255, 204), (255, 204, 0), 
                       (0, 255, 0), (255, 0, 255), (0, 255, 255)]
        gravity = DEFAULT_GRAVITY
        screen.fill((10, 10, 40))
    elif theme_name == "Space":
        # Space-themed
        BALL_COLORS = [(255, 255, 255), (255, 200, 100), (100, 200, 255), 
                       (255, 100, 100), (200, 100, 255)]
        gravity = DEFAULT_GRAVITY * 0.3  # Lower gravity
        # Draw stars
        screen.fill((0, 0, 20))
        for _ in range(100):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            size = random.randint(1, 3)
            pygame.draw.circle(screen, (255, 255, 255), (x, y), size)
    elif theme_name == "Underwater":
        # Water-themed blues and greens
        BALL_COLORS = [(0, 200, 255), (0, 255, 200), (0, 150, 255), 
                       (0, 255, 150), (100, 255, 255)]
        gravity = DEFAULT_GRAVITY * 0.7
        # Draw water background
        screen.fill((0, 0, 100))
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(20):
            y = random.randint(0, HEIGHT)
            pygame.draw.line(s, (100, 200, 255, 30), (0, y), (WIDTH, y+20), 5)
        screen.blit(s, (0, 0))
    elif theme_name == "Fire":
        # Fire-themed reds and oranges
        BALL_COLORS = [(255, 100, 0), (255, 50, 0), (255, 200, 0), 
                       (255, 150, 0), (255, 255, 0)]
        gravity = DEFAULT_GRAVITY * 1.2  # Higher gravity
        # Draw fire background
        screen.fill((40, 0, 0))

def draw_target(screen):
    if target_active:
        # Calculate a pulsing effect
        pulse = (math.sin(pygame.time.get_ticks() / 200) + 1) * 0.5
        outer_size = 20 + int(pulse * 5)
        
        # Draw outer circle (pulsing)
        pygame.draw.circle(screen, (255, 255, 0), target_position, outer_size, 2)
        # Draw inner circle
        pygame.draw.circle(screen, (255, 0, 0), target_position, 15)
        # Draw center
        pygame.draw.circle(screen, (255, 255, 255), target_position, 5)
        
        # Draw timer bar
        remaining = 1.0 - (target_timer / target_timeout)
        bar_width = 40
        pygame.draw.rect(screen, (100, 100, 100), 
                         (target_position[0] - bar_width/2, 
                          target_position[1] - 35, 
                          bar_width, 5))
        pygame.draw.rect(screen, (0, 255, 0), 
                         (target_position[0] - bar_width/2, 
                          target_position[1] - 35, 
                          bar_width * remaining, 5))

def spawn_target():
    global target_position, target_active, target_timer
    
    # Find a position away from the center and existing balls
    valid_position = False
    attempts = 0
    while not valid_position and attempts < 20:
        attempts += 1
        # Try to place target near the edges but not too close
        if random.random() < 0.5:
            x = random.randint(100, WIDTH - 100)
            if random.random() < 0.5:
                y = random.randint(50, 150)
            else:
                y = random.randint(HEIGHT - 150, HEIGHT - 50)
        else:
            y = random.randint(100, HEIGHT - 100)
            if random.random() < 0.5:
                x = random.randint(50, 150)
            else:
                x = random.randint(WIDTH - 150, WIDTH - 50)
                
        # Check if position is valid (not inside polygon and away from balls)
        valid_position = True
        center_dist = math.sqrt((x - WIDTH/2)**2 + (y - HEIGHT/2)**2)
        if center_dist < shape_radius + 50:
            valid_position = False
            continue
            
        for ball in balls:
            ball_dist = math.sqrt((x - ball.x)**2 + (y - ball.y)**2)
            if ball_dist < ball.radius + 50:
                valid_position = False
                break
    
    if valid_position:
        target_position = (x, y)
        target_active = True
        target_timer = 0

def draw_ui(screen, font):
    # Draw UI elements for adjusting parameters
    y_pos = 10
    line_height = 25
    
    if game_mode:
        # Draw score and time in game mode
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH - 120, 10))
        
        time_text = font.render(f"Time: {int(time_elapsed)}s", True, WHITE)
        screen.blit(time_text, (WIDTH - 120, 40))
    else:
        # Draw controls in sandbox mode
        controls = [
            f"Gravity: {gravity:.1f} [1/2]",
            f"Rotation: {rotation_speed:.2f} [3/4]",
            f"Elasticity: {elasticity:.2f} [5/6]",
            f"Friction: {friction:.2f} [7/8]",
            f"Sides: {polygon_sides} [9/0]",
            f"Size: {shape_radius} [+/-]",
            f"Auto Rotate: {'ON' if auto_rotate else 'OFF'} [Space]",
            f"Trails: {'ON' if show_trails else 'OFF'} [T]",
            f"Particles: {'ON' if enable_particle_effects else 'OFF'} [P]",
            f"Theme: {themes[current_theme]} [Tab]",
            f"Gravity Field: {'ON' if gravity_point_active else 'OFF'} [G]",
            "Add Ball [B]",
            "Game Mode [M]",
            "Reset [R]",
            "Quit [Esc]"
        ]
        
        for text in controls:
            text_surface = font.render(text, True, WHITE)
            screen.blit(text_surface, (10, y_pos))
            y_pos += line_height
    
    # Draw gravity point if active
    if gravity_point_active:
        # Draw concentric circles for gravity field
        for radius in range(10, 100, 20):
            alpha = 255 - radius * 2
            s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, 255, 255, alpha), (radius, radius), radius, 1)
            screen.blit(s, (gravity_point_pos[0] - radius, gravity_point_pos[1] - radius))
            
        pygame.draw.circle(screen, (0, 255, 255), gravity_point_pos, 5)

def reset_simulation():
    # Reset to default settings
    global gravity, rotation_speed, elasticity, friction, polygon_sides, balls, polygon
    global auto_rotate, shape_radius, score, game_mode, time_elapsed, target_active
    global show_trails, gravity_point_active, enable_particle_effects
    
    gravity = DEFAULT_GRAVITY
    rotation_speed = DEFAULT_ROTATION_SPEED
    elasticity = DEFAULT_ELASTICITY
    friction = DEFAULT_FRICTION
    polygon_sides = DEFAULT_SIDES
    auto_rotate = True
    shape_radius = 150
    show_trails = False
    gravity_point_active = False
    enable_particle_effects = True
    score = 0
    game_mode = False
    time_elapsed = 0
    target_active = False
    
    # Reset the polygon and balls
    polygon = Polygon(WIDTH/2, HEIGHT/2, shape_radius, polygon_sides)
    balls = [Ball(WIDTH/2, HEIGHT/2 - 50, 15, RED)]

def add_ball():
    if len(balls) < 20:  # Limit to 20 balls for performance
        color = random.choice(BALL_COLORS)
        radius = random.randint(10, 20)
        # Add some variation to starting positions
        offset_x = random.randint(-30, 30)
        offset_y = random.randint(-30, 0)
        ball = Ball(WIDTH/2 + offset_x, HEIGHT/2 - 50 + offset_y, radius, color)
        balls.append(ball)

def update_polygon():
    global polygon
    polygon = Polygon(WIDTH/2, HEIGHT/2, shape_radius, polygon_sides)

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Polygon Physics Playground")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 18)
game_font = pygame.font.SysFont('Arial', 36)

# Try to load sound effects
try:
    collision_sound = pygame.mixer.Sound("collision.wav")  # You would need to provide this file
    target_sound = pygame.mixer.Sound("target.wav")  # You would need to provide this file
    sound_available = True
    print("Sound effects loaded successfully.")
except Exception as e:
    sound_available = False
    print(f"Sound effects could not be loaded: {e}")
    print("The game will run without sound effects.")
    # Create dummy sound objects to avoid checking sound_available everywhere
    class DummySound:
        def play(self): pass
        def set_volume(self, vol): pass
    collision_sound = DummySound()
    target_sound = DummySound()

# Create objects
polygon = Polygon(WIDTH/2, HEIGHT/2, shape_radius, polygon_sides)
balls = [Ball(WIDTH/2, HEIGHT/2 - 50, 15, RED)]

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                reset_simulation()
            elif event.key == pygame.K_b:
                add_ball()
            elif event.key == pygame.K_SPACE:
                auto_rotate = not auto_rotate
            elif event.key == pygame.K_t:
                show_trails = not show_trails
            elif event.key == pygame.K_p:
                enable_particle_effects = not enable_particle_effects
            elif event.key == pygame.K_g:
                gravity_point_active = not gravity_point_active
            elif event.key == pygame.K_m:
                game_mode = not game_mode
                score = 0
                time_elapsed = 0
                if game_mode:
                    spawn_target()
            elif event.key == pygame.K_TAB:
                current_theme = (current_theme + 1) % len(themes)
            elif event.key == pygame.K_1:
                gravity = max(0, gravity - 100)
            elif event.key == pygame.K_2:
                gravity += 100
            elif event.key == pygame.K_3:
                rotation_speed = max(0.1, rotation_speed - 0.1)
            elif event.key == pygame.K_4:
                rotation_speed += 0.1
            elif event.key == pygame.K_5:
                elasticity = max(0.1, elasticity - 0.1)
            elif event.key == pygame.K_6:
                elasticity = min(1.0, elasticity + 0.1)
            elif event.key == pygame.K_7:
                friction = max(0.8, friction - 0.02)
            elif event.key == pygame.K_8:
                friction = min(1.0, friction + 0.02)
            elif event.key == pygame.K_9:
                polygon_sides = max(3, polygon_sides - 1)
                update_polygon()
            elif event.key == pygame.K_0:
                polygon_sides = min(12, polygon_sides + 1)
                update_polygon()
            elif event.key == pygame.K_MINUS:
                shape_radius = max(50, shape_radius - 10)
                update_polygon()
            elif event.key == pygame.K_EQUALS:  # This is the + key
                shape_radius = min(300, shape_radius + 10)
                update_polygon()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if not auto_rotate:
                    # Manual rotation with mouse
                    dx = mouse_x - polygon.center_x
                    dy = mouse_y - polygon.center_y
                    polygon.angle = math.atan2(dy, dx)
                elif gravity_point_active:
                    # Move gravity point
                    gravity_point_pos = (mouse_x, mouse_y)
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0] and gravity_point_active:  # Left button held
                # Update gravity point position when dragging
                gravity_point_pos = event.pos
    
    # Calculate delta time
    dt = clock.tick(FPS) / 1000.0
    
    # Update game timer
    if game_mode:
        time_elapsed += dt
        
        # Update target timer and check if we need a new target
        if target_active:
            target_timer += dt
            if target_timer >= target_timeout:
                target_active = False
        elif random.random() < 0.01:  # Small chance to spawn a new target
            spawn_target()
    
    # Update physics
    polygon.update(dt)
    for i, ball in enumerate(balls):
        ball.update(dt)
        polygon.check_collision(ball)
        
        # Check for target collision
        if game_mode and ball.check_target_collision():
            target_active = False
            score += 10
            if sound_available:
                target_sound.play()
            
            # Create particles at target position
            if enable_particle_effects:
                for _ in range(20):
                    ball.particles.append(Particle(target_position[0], target_position[1], (255, 255, 0)))
        
        # Ball-to-ball collisions
        for j in range(i + 1, len(balls)):
            other = balls[j]
            dx = other.x - ball.x
            dy = other.y - ball.y
            dist = math.sqrt(dx*dx + dy*dy)
            min_dist = ball.radius + other.radius
            
            if dist < min_dist:
                # Calculate collision response
                angle = math.atan2(dy, dx)
                
                # Normalize direction
                nx = dx / dist
                ny = dy / dist
                
                # Calculate relative velocity
                rv_x = other.vel_x - ball.vel_x
                rv_y = other.vel_y - ball.vel_y
                
                # Calculate relative velocity in terms of the normal direction
                vel_along_normal = rv_x * nx + rv_y * ny
                
                # Do not resolve if velocities are separating
                if vel_along_normal > 0:
                    continue
                
                # Calculate restitution (elasticity)
                e = elasticity
                
                # Calculate impulse scalar
                j = -(1 + e) * vel_along_normal
                j /= 1/ball.mass + 1/other.mass
                
                # Apply impulse
                impulse_x = j * nx
                impulse_y = j * ny
                
                # Apply impulse based on mass
                ball.vel_x -= impulse_x / ball.mass
                ball.vel_y -= impulse_y / ball.mass
                other.vel_x += impulse_x / other.mass
                other.vel_y += impulse_y / other.mass
                
                # Move balls apart to prevent sticking
                overlap = min_dist - dist
                move_x = overlap * nx * 0.5
                move_y = overlap * ny * 0.5
                
                ball.x -= move_x
                ball.y -= move_y
                other.x += move_x
                other.y += move_y
                
                # Set collision flags and effects
                ball.is_colliding = True
                other.is_colliding = True
                ball.collision_time = 0.1
                other.collision_time = 0.1
                
                # Add collision particles between the balls
                if enable_particle_effects:
                    collision_point_x = ball.x + nx * ball.radius
                    collision_point_y = ball.y + ny * ball.radius
                    for _ in range(8):
                        particle_color = random.choice([ball.color, other.color])
                        ball.particles.append(Particle(collision_point_x, collision_point_y, particle_color))
                
                # Play collision sound
                if sound_available and random.random() < 0.3:  # Limit sound frequency
                    collision_sound.set_volume(min(1.0, dist / 100))
                    collision_sound.play()
    
    # Draw
    # Apply current theme background
    apply_theme(themes[current_theme])
    
    # Draw gravity point if active
    if gravity_point_active:
        draw_ui(screen, font)  # This includes drawing the gravity point
    else:
        draw_ui(screen, font)
    
    # Draw target in game mode
    if game_mode and target_active:
        draw_target(screen)
        
    # Draw polygon
    polygon.draw(screen)
    
    # Draw balls
    for ball in balls:
        ball.draw(screen)
    
    # Draw game over screen if in game mode and time is up
    if game_mode and time_elapsed >= 60:  # 60 second game
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (0, 0))
        
        game_over_text = game_font.render("GAME OVER", True, WHITE)
        score_text = game_font.render(f"Final Score: {score}", True, WHITE)
        instruction_text = font.render("Press 'M' to play again or 'R' to reset", True, WHITE)
        
        screen.blit(game_over_text, 
                   (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 60))
        screen.blit(score_text, 
                   (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        screen.blit(instruction_text, 
                   (WIDTH//2 - instruction_text.get_width()//2, HEIGHT//2 + 60))
    
    pygame.display.flip()

# Clean up resources
try:
    pygame.quit()
    print("Game exited successfully.")
except Exception as e:
    print(f"Error during cleanup: {e}")