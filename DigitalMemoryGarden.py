import pygame
import random
import datetime
import json
import math
from pygame import gfxdraw

class Memory:
    def __init__(self, text, date=None):
        self.text = text
        self.date = date or datetime.datetime.now()
        self.last_visited = self.date
        self.visits = 1
        self.position = (random.randint(100, 700), random.randint(100, 500))
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        self.size = 5  # Initial size
        
    def visit(self):
        self.visits += 1
        self.last_visited = datetime.datetime.now()
    
    def get_age(self):
        return (datetime.datetime.now() - self.date).days
    
    def get_vitality(self):
        # How "alive" is this memory based on recency and frequency
        recency = 1 / (1 + (datetime.datetime.now() - self.last_visited).days)
        return min(1.0, (self.visits * 0.2 * recency) + 0.1)
    
    def get_display_size(self):
        vitality = self.get_vitality()
        return int(self.size + (vitality * 30))
        
    def draw(self, screen):
        vitality = self.get_vitality()
        size = self.get_display_size()
        
        # Draw stem
        stem_height = int(size * 2.5)
        stem_start = (self.position[0], self.position[1] + size)
        stem_end = (self.position[0], self.position[1] + size + stem_height)
        pygame.draw.line(screen, (0, 150, 0), stem_start, stem_end, 2)
        
        # Draw flower/plant
        adjusted_color = tuple(int(c * vitality) for c in self.color)
        pygame.draw.circle(screen, adjusted_color, self.position, size)
        
        # Draw center
        pygame.draw.circle(screen, (255, 255, 150), self.position, size // 3)

class MemoryGarden:
    def __init__(self):
        pygame.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Memory Garden")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 16)
        self.memories = []
        self.selected_memory = None
        self.input_active = False
        self.input_text = ""
        self.try_load_memories()
        
    def try_load_memories(self):
        try:
            with open("memories.json", "r") as f:
                memory_data = json.load(f)
                for m in memory_data:
                    memory = Memory(m["text"])
                    memory.date = datetime.datetime.fromisoformat(m["date"])
                    memory.last_visited = datetime.datetime.fromisoformat(m["last_visited"])
                    memory.visits = m["visits"]
                    memory.position = tuple(m["position"])
                    memory.color = tuple(m["color"])
                    self.memories.append(memory)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create some sample memories if no file exists
            self.memories = [
                Memory("First day of college"),
                Memory("Trip to the mountains"),
                Memory("Learning to play guitar")
            ]
    
    def save_memories(self):
        memory_data = []
        for memory in self.memories:
            memory_data.append({
                "text": memory.text,
                "date": memory.date.isoformat(),
                "last_visited": memory.last_visited.isoformat(),
                "visits": memory.visits,
                "position": memory.position,
                "color": memory.color
            })
        with open("memories.json", "w") as f:
            json.dump(memory_data, f)
    
    def add_memory(self, text):
        self.memories.append(Memory(text))
        self.save_memories()
    
    def run(self):
        running = True
        while running:
            self.screen.fill((50, 100, 50))  # Dark green background
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.input_active:
                            self.input_active = False
                            if self.input_text.strip():
                                self.add_memory(self.input_text)
                                self.input_text = ""
                        else:
                            # Check if clicked on a memory
                            for memory in self.memories:
                                distance = math.sqrt((event.pos[0] - memory.position[0])**2 + 
                                                   (event.pos[1] - memory.position[1])**2)
                                if distance <= memory.get_display_size():
                                    memory.visit()
                                    self.selected_memory = memory
                                    self.save_memories()
                                    break
                            else:
                                self.selected_memory = None
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:  # Press 'n' to create new memory
                        self.input_active = True
                        self.input_text = ""
                    elif self.input_active:
                        if event.key == pygame.K_RETURN:
                            self.input_active = False
                            if self.input_text.strip():
                                self.add_memory(self.input_text)
                                self.input_text = ""
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        else:
                            self.input_text += event.unicode
            
            # Draw ground
            pygame.draw.rect(self.screen, (139, 69, 19), (0, 500, 800, 100))
            
            # Draw memories
            for memory in self.memories:
                memory.draw(self.screen)
            
            # Draw selected memory info
            if self.selected_memory:
                text_surface = self.font.render(self.selected_memory.text, True, (255, 255, 255))
                visits_text = self.font.render(f"Visits: {self.selected_memory.visits}", True, (255, 255, 255))
                date_text = self.font.render(f"Created: {self.selected_memory.date.strftime('%Y-%m-%d')}", True, (255, 255, 255))
                
                self.screen.blit(text_surface, (20, 20))
                self.screen.blit(visits_text, (20, 40))
                self.screen.blit(date_text, (20, 60))
            
            # Draw input box
            if self.input_active:
                pygame.draw.rect(self.screen, (0, 0, 0), (50, 550, 700, 30))
                pygame.draw.rect(self.screen, (255, 255, 255), (50, 550, 700, 30), 2)
                text_surface = self.font.render(self.input_text, True, (255, 255, 255))
                self.screen.blit(text_surface, (55, 555))
            
            # Draw instructions
            if not self.input_active and not self.selected_memory:
                instructions = self.font.render("Click on memories to revisit them. Press 'n' to create a new memory.", True, (255, 255, 255))
                self.screen.blit(instructions, (20, 20))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        self.save_memories()

if __name__ == "__main__":
    garden = MemoryGarden()
    garden.run()