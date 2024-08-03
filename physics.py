import pygame
import asyncio
import pymunk
import pymunk.pygame_util
import math
import random

pygame.init()

WIDTH, HEIGHT = 1000, 800
window = pygame.display.set_mode((WIDTH, HEIGHT))

def calculate_distance(p1,p2):
    return math.sqrt((p2[1] - p1[1])**2 + (p2[0] - p1[0])**2)

def calculate_angle(p1,p2):
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])

def draw(space, window, draw_options, line):
    window.fill("white")




    if line:
        pygame.draw.line(window,"black",line[0],line[1],3)
    space.debug_draw(draw_options)


    pygame.display.update()


def create_boundaries(space, width, height):
    rectangles = [
        [(width/2,height - 10), (width,20)],
        [(width/2,10), (width,20)],
        [(10,height/2), (20,height)],
        [(width - 10, height / 2), (20,height)]]
    
    for pos,size in rectangles:
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Poly.create_box(body,size)
        shape.elasticity = 0.3
        shape.friction = 0.5
        space.add(body,shape)

def create_structure(space, width, height):
    # Generate small balls (circles) every 20 pixels across the entire game window
    ball_radius = 7
    ball_mass = 5
    ball_color = (0, 0, 255, 255)  # Blue color

    for x in range(0, width, 20):
        for y in range(0, height, 20):
            body = pymunk.Body()
            body.position = (x, y)
            shape = pymunk.Circle(body, ball_radius)
            shape.mass = ball_mass
            shape.color = ball_color
            shape.elasticity = 0.5
            shape.friction = 0.5
            space.add(body, shape)


def create_ball(space, radius, mass, position):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = position
    shape = pymunk.Circle(body, radius)
    shape.mass = mass
    shape.color = (200, 60, 0, 100)
    body.damping = .5  # Increased linear damping
    body.angular_damping = 0.8  # Increased angular damping
    shape.elasticity = 0.5
    shape.friction = 0.5
    space.add(body, shape)
    return shape



async def main(window, width, height):
    run = True
    clock = pygame.time.Clock()
    fps = 60
    dt = 1 / fps

    space = pymunk.Space()
    space.gravity = (0, -980)

    create_boundaries(space,width,height)
    create_structure(space,width,height)

    draw_options = pymunk.pygame_util.DrawOptions(window)

    pressed_pos = None
    ball = None

    while run:
        line = None
        if ball and pressed_pos:
            line = [pressed_pos, pygame.mouse.get_pos()]


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
                

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not ball:
                    pressed_pos = pygame.mouse.get_pos()
                    ball = create_ball(space,30,1000, pressed_pos)
                elif pressed_pos:
                    ball.body.body_type=pymunk.Body.DYNAMIC
                    angle = calculate_angle(*line)
                    force = calculate_distance(*line) * 5000
                    fx = math.cos(angle) * force
                    fy = math.sin(angle) * force
                    ball.body.apply_impulse_at_local_point((-fx,-fy), (0,0))
                    pressed_pos = None
                else:
                    space.remove(ball,ball.body)
                    ball = None
                    pressed_pos = None


        draw(space, window, draw_options, line)
        space.step(dt)
        clock.tick(fps)
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main(window,WIDTH,HEIGHT))