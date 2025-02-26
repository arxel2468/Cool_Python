# particles.py

import pygame
import random
import numpy as np

class Particle:
    def __init__(self, position, velocity, color, size, bounds):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.acceleration = np.zeros(2)
        self.color = color
        self.size = size
        self.bounds = bounds

    def apply_force(self, force):
        self.acceleration += force

    def update(self):
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration *= 0

        # Bounce off walls
        for i in [0, 1]:
            if self.position[i] <= 0 or self.position[i] >= self.bounds[i]:
                self.velocity[i] *= -1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position.astype(int), self.size)

class ParticleSystem:
    def __init__(self, num_particles, bounds):
        self.particles = []
        self.bounds = bounds
        self.attract_point = np.array(bounds) / 2
        for _ in range(num_particles):
            position = np.random.rand(2) * bounds
            velocity = np.random.uniform(-1, 1, size=2)
            color = [random.randint(0, 255) for _ in range(3)]
            size = random.randint(2, 5)
            particle = Particle(position, velocity, color, size, bounds)
            self.particles.append(particle)

    def update(self):
        for i, particle in enumerate(self.particles):
            # Attraction to center
            direction = self.attract_point - particle.position
            distance = np.linalg.norm(direction)
            force = direction / distance if distance != 0 else np.zeros(2)
            particle.apply_force(force * 0.05)

            # Repulsion from other particles
            for other in self.particles[i+1:]:
                direction = particle.position - other.position
                distance = np.linalg.norm(direction)
                if distance < 20 and distance != 0:
                    force = direction / distance
                    particle.apply_force(force * 0.1)
                    other.apply_force(-force * 0.1)

            particle.update()

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

    def set_attract_point(self, position):
        self.attract_point = np.array(position)
