import pygame
import sys
import random

# Game Constants
RESOLUTION = (576, 1024)
CLOCK_TICK = 120

# Set Pygame
pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=512)
pygame.init()
screen = pygame.display.set_mode(RESOLUTION)
clock = pygame.time.Clock()
game_font = pygame.font.Font("Assets/Fonts/04B_19.ttf", 40)

# Game Variables
gravity = 0.25
bird_movement = 0
game_active = False
game_speed = 3
score = 0
high_score = 0

# Assets - Images
"Background Sprite"
bg_surface = pygame.image.load("Assets/Sprites/background-day.png").convert()
bg_surface = pygame.transform.scale2x(bg_surface)
bg_x_pos = 0
bg_y_pos = 0

"Floor"
floor_surface = pygame.image.load("Assets/Sprites/base.png").convert()
floor_surface = pygame.transform.scale2x(floor_surface)
floor_x_pos = 0
floor_y_pos = 900

"Bird"
bird_downflap = pygame.transform.scale2x(pygame.image.load("Assets/Sprites/yellowbird-downflap.png").convert_alpha())
bird_midflap = pygame.transform.scale2x(pygame.image.load("Assets/Sprites/yellowbird-midflap.png").convert_alpha())
bird_upflap = pygame.transform.scale2x(pygame.image.load("Assets/Sprites/yellowbird-upflap.png").convert_alpha())
bird_frames = [bird_downflap, bird_midflap, bird_upflap]
bird_index = 0
bird_surface = bird_frames[bird_index]
bird_center = (100, 512)
bird_rect = bird_surface.get_rect(center=bird_center)

BIRDFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP, 200)

"Pipes"
pipe_surface = pygame.image.load("Assets/Sprites/pipe-green.png")
pipe_surface = pygame.transform.scale2x(pipe_surface)
pipe_list = []
SPAWN_PIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWN_PIPE, 1200)
pipe_heights = [400, 600, 800]

"Game Over"
game_over_surface = pygame.transform.scale2x(pygame.image.load("Assets/Sprites/message.png").convert_alpha())
game_over_rect = game_over_surface.get_rect(center=(288, 512))

# Assets - Music
"Flap"
flap_sound = pygame.mixer.Sound("Assets/SoundEffects/sfx_wing.wav")

"Death"
death_sound = pygame.mixer.Sound("Assets/SoundEffects/sfx_hit.wav")

"Score"
score_sound = pygame.mixer.Sound("Assets/SoundEffects/sfx_point.wav")


# Game methods
def draw_floor():
    global floor_x_pos

    floor_x_pos -= game_speed

    screen.blit(floor_surface, (floor_x_pos, floor_y_pos))
    screen.blit(floor_surface, (floor_x_pos + 576, floor_y_pos))

    if floor_x_pos <= -576:
        floor_x_pos = 0


def create_pipe():
    random_pipe_pos = random.choice(pipe_heights)
    bottom_pipe = pipe_surface.get_rect(midtop=(700, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom=(700, random_pipe_pos - 300))

    return bottom_pipe, top_pipe


def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= game_speed

    return pipes


def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 1024:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)


def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            death_sound.play()
            return False

    if bird_rect.top <= -100 or bird_rect.bottom >= 900:
        death_sound.play()
        return False

    return True


def rotate_bird(bird):
    new_bird = pygame.transform.rotozoom(bird, -bird_movement * 3, 1)
    return new_bird


def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center=(100, bird_rect.centery))
    return new_bird, new_bird_rect


def display_score():
    global score
    global high_score
    global game_active

    if game_active is True:
        score += 0.1

    if score > high_score:
        high_score = score

    score_surface = game_font.render(f"Score: {int(score)}", True, (255, 255, 255))
    score_rect = score_surface.get_rect(center=(288, 100))
    screen.blit(score_surface, score_rect)

    if game_active is False:
        high_score_surface = game_font.render(f"Highest Score: {int(high_score)}", True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(288, 850))
        screen.blit(high_score_surface, high_score_rect)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_movement = 0
                bird_movement -= 8
                flap_sound.play()

            if event.key == pygame.K_SPACE and game_active is False:
                game_active = True
                pipe_list.clear()
                bird_rect.center = bird_center
                bird_movement = 0
                score = 0

        if event.type == SPAWN_PIPE:
            pipe_list.extend(create_pipe())

        if event.type == BIRDFLAP:
            if bird_index < 2:
                bird_index += 1
            else:
                bird_index = 0

            bird_surface, bird_rect = bird_animation()

    # Background
    screen.blit(bg_surface, (bg_x_pos, bg_y_pos))

    if game_active:
        # Bird
        bird_movement += gravity
        rotated_bird = rotate_bird(bird_surface)
        bird_rect.centery += bird_movement
        screen.blit(rotated_bird, bird_rect)
        game_active = check_collision(pipe_list)

        # Pipes
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)
    else:
        screen.blit(game_over_surface, game_over_rect)

    # Floor
    draw_floor()

    # Score
    display_score()

    pygame.display.update()
    clock.tick(CLOCK_TICK)
