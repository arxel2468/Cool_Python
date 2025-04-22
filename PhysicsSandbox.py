import pygame
import pymunk
import pymunk.pygame_util
import random

pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
draw_options = pymunk.pygame_util.DrawOptions(screen)

space = pymunk.Space()
space.gravity = (0, 900)

def add_ball(pos, radius=25):
    mass = 1
    moment = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, moment)
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.elasticity = 0.8
    shape.friction = 0.6
    shape.color = pygame.Color(random.randint(100,255),random.randint(100,255),random.randint(100,255))
    space.add(body, shape)
    return body, shape

# Static floor
floor = pymunk.Segment(space.static_body, (0, HEIGHT-30), (WIDTH, HEIGHT-30), 5)
floor.elasticity = 0.9
space.add(floor)

objects = []
dragged = None
offset = (0,0)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for b, shape in objects:
                if shape.point_query(mouse_pos).distance < 0:
                    dragged = b
                    offset = b.position - mouse_pos
                    break
            else:
                # Add new ball
                obj = add_ball(mouse_pos)
                objects.append(obj)

        elif event.type == pygame.MOUSEBUTTONUP:
            dragged = None

    if dragged:
        mouse_pos = pygame.mouse.get_pos()
        dragged.position = mouse_pos + offset
        dragged.velocity = (0,0)

    screen.fill((18,18,22))
    space.debug_draw(draw_options)
    pygame.display.flip()
    space.step(1/60.0)
    clock.tick(60)

pygame.quit()