import random
import pygame
import asyncio
import pymunk
import pymunk.pygame_util
import math

pygame.init()

WIDTH, HEIGHT = 1000, 800
window = pygame.display.set_mode((WIDTH, HEIGHT))

def calculate_distance(p1, p2):
    return math.sqrt((p2[1] - p1[1])**2 + (p2[0] - p1[0])**2)

def calculate_angle(p1, p2):
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])

def draw(space, window, draw_options, line, timer, player_square, player_image, blue_balls, background_image,level):
    window.blit(background_image, (0, 0))  # Draw the background image

    # Define border properties
    border_thickness = 20
    corner_radius = 40
    border_color = (139, 69, 19)  # Brown color for the fence

    # Draw top border (excluding corners)
    pygame.draw.rect(window, border_color, pygame.Rect(0, 0, WIDTH, border_thickness))  # Full top border
    pygame.draw.rect(window, background_image.get_at((0, 0)), pygame.Rect(0, 0, corner_radius, corner_radius))  # Top-left corner cutout
    pygame.draw.rect(window, background_image.get_at((WIDTH - corner_radius, 0)), pygame.Rect(WIDTH - corner_radius, 0, corner_radius, corner_radius))  # Top-right corner cutout

    # Draw bottom border (excluding corners)
    pygame.draw.rect(window, border_color, pygame.Rect(0, HEIGHT - border_thickness, WIDTH, border_thickness))  # Full bottom border
    pygame.draw.rect(window, background_image.get_at((0, HEIGHT - corner_radius)), pygame.Rect(0, HEIGHT - corner_radius, corner_radius, corner_radius))  # Bottom-left corner cutout
    pygame.draw.rect(window, background_image.get_at((WIDTH - corner_radius, HEIGHT - corner_radius)), pygame.Rect(WIDTH - corner_radius, HEIGHT - corner_radius, corner_radius, corner_radius))  # Bottom-right corner cutout

    # Draw left border (excluding corners)
    pygame.draw.rect(window, border_color, pygame.Rect(0, border_thickness, border_thickness, HEIGHT - 2 * border_thickness))  # Full left border
    pygame.draw.rect(window, background_image.get_at((0, border_thickness)), pygame.Rect(0, border_thickness, corner_radius, corner_radius))  # Top-left corner cutout
    pygame.draw.rect(window, background_image.get_at((0, HEIGHT - border_thickness - corner_radius)), pygame.Rect(0, HEIGHT - border_thickness - corner_radius, corner_radius, corner_radius))  # Bottom-left corner cutout

    # Draw right border (excluding corners)
    pygame.draw.rect(window, border_color, pygame.Rect(WIDTH - border_thickness, border_thickness, border_thickness, HEIGHT - 2 * border_thickness))  # Full right border
    pygame.draw.rect(window, background_image.get_at((WIDTH - corner_radius, border_thickness)), pygame.Rect(WIDTH - corner_radius, border_thickness, corner_radius, corner_radius))  # Top-right corner cutout
    pygame.draw.rect(window, background_image.get_at((WIDTH - corner_radius, HEIGHT - border_thickness - corner_radius)), pygame.Rect(WIDTH - corner_radius, HEIGHT - border_thickness - corner_radius, corner_radius, corner_radius))  # Bottom-right corner cutout

    # Draw the player image
    player_rect = player_image.get_rect(center=(player_square.body.position[0], player_square.body.position[1]))
    window.blit(player_image, player_rect.topleft)

    # Draw blue balls
    for shape, image in blue_balls:
        position = shape.body.position
        rect = image.get_rect(center=(position[0], position[1]))
        window.blit(image, rect.topleft)

    # Display timer on screen
    font = pygame.font.SysFont(None, 36)
    timer_text = font.render(f"Time: {int(timer)}", True, (0, 0, 0))
    window.blit(timer_text, (10, 10))

    level_text = font.render(f"Level: {level}", True, (0, 0, 0))
    window.blit(level_text, (WIDTH - 150, 10))  # Adjust the position as needed

    pygame.display.update()


def create_boundaries(space, width, height):
    border_thickness = 20
    color = (139, 69, 19)

    rectangles = [
        [(width / 2, border_thickness / 2), (width, border_thickness)],
        [(width / 2, height - border_thickness / 2), (width, border_thickness)],
        [(border_thickness / 2, height / 2), (border_thickness, height)],
        [(width - border_thickness / 2, height / 2), (border_thickness, height)]
    ]

    for pos, size in rectangles:
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Poly.create_box(body, size)
        shape.elasticity = 0.3
        shape.friction = 0.5
        shape.collision_type = 1
        shape.color = color
        space.add(body, shape)

    corner_radius = border_thickness / 2
    corner_positions = [
        (0, 0),
        (width, 0),
        (0, height),
        (width, height)
    ]

    for pos in corner_positions:
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Circle(body, corner_radius)
        shape.elasticity = 0.3
        shape.friction = 0.5
        shape.collision_type = 1
        shape.color = (0, 0, 0, 0)
        space.add(body, shape)

def create_squares(space, width, height):
    square_size = 60
    color = (100, 30, 100, 255)

    positions = [
        (square_size // 2, square_size // 2),
        (width - square_size // 2, square_size // 2),
        (square_size // 2, height - square_size // 2),
        (width - square_size // 2, height - square_size // 2)
    ]

    for pos in positions:
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Poly.create_box(body, (square_size, square_size))
        shape.color = color
        shape.elasticity = 0.5
        shape.friction = 0.5
        shape.collision_type = 2
        space.add(body, shape)

def create_structure(space, width, height, sheep_image, level):
    ball_radius = 20
    ball_mass = 100
    num_balls = 6 + level * 2  # Increase the number of balls with each level

    blue_balls = []
    for _ in range(num_balls):
        x = random.randint(ball_radius, width - ball_radius)
        y = random.randint(ball_radius, height - ball_radius)
        
        body = pymunk.Body()
        body.position = (x, y)
        
        # Create shape
        shape = pymunk.Circle(body, ball_radius)
        shape.mass = ball_mass
        shape.elasticity = 0.5
        shape.friction = 0.5
        shape.collision_type = 3
        
        # Add random initial velocity
        velocity_x = random.uniform(-100 - level * 10, 100 + level * 10)  # Increase speed with each level
        velocity_y = random.uniform(-100 - level * 10, 100 + level * 10)
        body.velocity = (velocity_x, velocity_y)
        
        space.add(body, shape)
        blue_balls.append((shape, sheep_image))
    
    return blue_balls



def create_ball(space, radius, mass, position):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = position
    shape = pymunk.Circle(body, radius)
    shape.mass = mass
    shape.color = (200, 60, 0, 255)
    body.damping = 1
    body.angular_damping = 1
    shape.elasticity = 0.5
    shape.friction = 0.7
    shape.collision_type = 4
    space.add(body, shape)
    return shape

def create_player_square(space, width, height):
    square_size = 50
    mass = 10
    moment = pymunk.moment_for_box(mass, (square_size, square_size))
    body = pymunk.Body(mass, moment)
    body.position = (width / 2, height / 2)
    shape = pymunk.Poly.create_box(body, (square_size, square_size))
    shape.elasticity = 0.5
    shape.friction = 0.7
    shape.collision_type = 5
    space.add(body, shape)
    body.moment = pymunk.moment_for_box(1e6, (square_size, square_size))
    body.damping = 0.5
    return shape

def handle_collision(arbiter, space, data):
    ball_shape, square_shape = arbiter.shapes
    if ball_shape.collision_type == 3 and square_shape.collision_type == 2:
        space.remove(ball_shape, ball_shape.body)
        for shape, _ in data['blue_balls']:
            if shape == ball_shape:
                data['blue_balls'].remove((shape, _))
                break
    return True

def handle_player_movement(player_square):
    keys = pygame.key.get_pressed()
    speed = 300

    velocity_x = 0
    velocity_y = 0

    if keys[pygame.K_LEFT]:
        velocity_x -= speed
    if keys[pygame.K_RIGHT]:
        velocity_x += speed
    if keys[pygame.K_UP]:
        velocity_y -= speed
    if keys[pygame.K_DOWN]:
        velocity_y += speed

    magnitude = math.sqrt(velocity_x**2 + velocity_y**2)
    if magnitude > 0:
        velocity_x /= magnitude
        velocity_y /= magnitude
        velocity_x *= speed
        velocity_y *= speed

    body = player_square.body
    body.velocity = (velocity_x, velocity_y)

async def main(window, width, height):
    try:
        level = 1
        max_level = 10  # Define a maximum level
        run = True
        clock = pygame.time.Clock()
        fps = 60
        dt = 1 / fps

        space = pymunk.Space()
        space.gravity = (0, 0)

        player_image = pygame.image.load('dog.png')
        player_image = pygame.transform.scale(player_image, (75, 75))
        sheep_image = pygame.image.load('sheep.png')
        sheep_image = pygame.transform.scale(sheep_image, (75, 75))
        background_image = pygame.image.load('grass.jpg')
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

        while run and level <= max_level:
            # Initialize level
            space = pymunk.Space()
            space.gravity = (0, 0)
            create_boundaries(space, width, height)
            create_squares(space, width, height)
            blue_balls = create_structure(space, width, height, sheep_image, level)
            player_square = create_player_square(space, width, height)

            draw_options = pymunk.pygame_util.DrawOptions(window)

            pressed_pos = None
            ball = None
            start_time = pygame.time.get_ticks()

            collision_handler = space.add_collision_handler(3, 2)
            
            def collision_callback(arbiter, space, _):
                handle_collision(arbiter, space, {'blue_balls': blue_balls})
                return True

            collision_handler.pre_solve = collision_callback

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
                            ball = create_ball(space, 30, 100, pressed_pos)
                        elif pressed_pos:
                            ball.body.body_type = pymunk.Body.DYNAMIC
                            angle = calculate_angle(*line)
                            force = calculate_distance(*line) * 700
                            fx = math.cos(angle) * force
                            fy = math.sin(angle) * force
                            ball.body.apply_impulse_at_local_point((-fx, -fy), (0, 0))
                            pressed_pos = None
                        else:
                            space.remove(ball, ball.body)
                            ball = None
                            pressed_pos = None

                handle_player_movement(player_square)

                # Update the countdown timer
                elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0
                time_remaining = max(0, 30 - elapsed_time)

                # Check if time has expired
                if time_remaining <= 0:
                    if blue_balls:
                        font = pygame.font.SysFont(None, 72)
                        text = font.render('You Lose!', True, (0, 0, 0))
                        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                        window.blit(text, text_rect)
                        pygame.display.update()
                        await asyncio.sleep(2)
                    run = False
                    break

                # Check if all blue balls are gone
                elif not blue_balls:
                    font = pygame.font.SysFont(None, 72)
                    text = font.render('You Win!', True, (0, 0, 0))
                    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                    window.blit(text, text_rect)
                    pygame.display.update()
                    await asyncio.sleep(2)
                    level += 1  # Move to the next level
                    break  # Break out of the current level loop

                draw(space, window, draw_options, line, time_remaining, player_square, player_image, blue_balls, background_image, level)
                space.step(dt)
                clock.tick(fps)
                await asyncio.sleep(0)

        if level > max_level:
            font = pygame.font.SysFont(None, 72)
            text = font.render('You Win All Levels!', True, (0, 0, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            window.blit(text, text_rect)
            pygame.display.update()
            await asyncio.sleep(2)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.quit()


if __name__ == "__main__":
    asyncio.run(main(window, WIDTH, HEIGHT))