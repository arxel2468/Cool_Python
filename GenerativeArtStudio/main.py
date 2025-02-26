# main.py

import pygame
from fractals import mandelbrot, julia
from particles import ParticleSystem
from color_harmony import generate_palette
from utils import ensure_output_dir, get_timestamp
from exporters import export_to_svg
from gui import ControlPanel
import sys
from threading import Thread
from PyQt5.QtWidgets import QApplication

def main():
    # Initialize Pygame and PyQt5
    pygame.init()
    app = QApplication(sys.argv)
    control_panel = ControlPanel()
    control_panel.show()

    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("Generative Art Studio")

    # Initial Settings
    settings = control_panel.get_settings()
    palette = generate_palette(settings['harmony'])
    fractal_surface = generate_fractal_surface(settings)

    # Particle System
    particle_system = ParticleSystem(num_particles=200, bounds=(screen_width, screen_height))

    # Main Loop
    clock = pygame.time.Clock()
    running = True
    frame_count = 0
    frames = []

    # Event Processing in a Separate Thread
    def process_events():
        nonlocal running, settings, palette, fractal_surface
        while running:
            app.processEvents()
            new_settings = control_panel.get_settings()
            if new_settings != settings:
                settings = new_settings
                palette = generate_palette(settings['harmony'])
                fractal_surface = generate_fractal_surface(settings)
            pygame.time.wait(10)

    event_thread = Thread(target=process_events)
    event_thread.start()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Interactive Controls
            elif event.type == pygame.MOUSEMOTION:
                particle_system.set_attract_point(event.pos)

            elif event.type == pygame.VIDEORESIZE:
                screen_width, screen_height = event.size
                screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
                particle_system.bounds = (screen_width, screen_height)

        # Update Particle System
        particle_system.update()

        # Draw Fractal Background
        screen.blit(fractal_surface, (0, 0))

        # Draw Particles
        particle_system.draw(screen)

        # Update Display
        pygame.display.flip()

        # Save frames for animation
        if frame_count % 5 == 0:
            frame_str = pygame.image.tostring(screen, 'RGB')
            frames.append(frame_str)

        frame_count += 1
        clock.tick(30)

    # Export Outputs
    output_dir = ensure_output_dir()
    timestamp = get_timestamp()
    image_path = f"{output_dir}/art_{timestamp}.png"
    svg_path = f"{output_dir}/art_{timestamp}.svg"
    pygame.image.save(screen, image_path)
    export_to_svg(screen, svg_path)
    print(f"Artwork saved to {image_path} and {svg_path}")

    create_animation(frames, screen_width, screen_height, output_dir, timestamp)

    pygame.quit()
    sys.exit()

def generate_fractal_surface(settings):
    fractal_width, fractal_height = 800, 600
    zoom = settings['zoom']
    max_iter = settings['max_iter']
    fractal_type = settings['fractal_type']

    if fractal_type == 'Julia':
        c_complex = complex(-0.7, 0.27015)
        fractal_img = julia(fractal_width, fractal_height, zoom, max_iter, c_complex)
    else:
        fractal_img = mandelbrot(fractal_width, fractal_height, zoom, max_iter)

    fractal_surface = pygame.image.fromstring(fractal_img.tobytes(), fractal_img.size, fractal_img.mode)
    return fractal_surface

def create_animation(frames, width, height, output_dir, timestamp):
    from moviepy.editor import ImageSequenceClip
    import numpy as np

    images = []
    for frame_str in frames:
        img = pygame.image.fromstring(frame_str, (width, height), 'RGB')
        img_array = pygame.surfarray.array3d(img)
        img_array = np.transpose(img_array, (1, 0, 2))
        images.append(img_array)

    clip = ImageSequenceClip(images, fps=30)
    animation_path = f"{output_dir}/animation_{timestamp}.mp4"
    clip.write_videofile(animation_path, codec='libx264')
    print(f"Animation saved to {animation_path}")

if __name__ == "__main__":
    main()
