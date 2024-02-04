import random
import sys
import pygame
from pygame.locals import *

# Global Variables for the game
FPS = 60
SCREENWIDTH = 360
SCREENHEIGHT = 640
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUND_Y = SCREENHEIGHT * 0.85
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'gallery/sprites/bird.png'
BACKGROUND = 'gallery/sprites/background.png'
PIPE = 'gallery/sprites/pipe.png'


def welcome_screen():
    """
    Shows welcome images on the screen
    """

    player_x = int((SCREENWIDTH - GAME_SPRITES['player'].get_width()) / 2)
    player_y = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height()) / 7 * 5)
    message_x = int((SCREENWIDTH - GAME_SPRITES['message'].get_width()) / 2)
    message_y = int(SCREENHEIGHT * 0.13)
    base_x = 0
    while True:
        for event in pygame.event.get():
            # if user clicks on cross button, close the game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # If the user presses space or up key or left clicks, start the game for them
            elif (event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP)) or (
                    event.type == MOUSEBUTTONDOWN and event.button == 1):
                return
            else:
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))
                SCREEN.blit(GAME_SPRITES['message'], (message_x, message_y))
                SCREEN.blit(GAME_SPRITES['player'], (player_x, player_y))
                SCREEN.blit(GAME_SPRITES['base'], (base_x, GROUND_Y))
                pygame.display.update()
                FPS_CLOCK.tick(FPS)


def main_game():
    score = 0
    player_x = int(SCREENWIDTH / 5)
    player_y = int(SCREENWIDTH / 2)
    base_x = 0

    # Create 2 pipes for blitting on the screen
    new_pipe1 = get_random_pipe()
    new_pipe2 = get_random_pipe()

    # my List of upper pipes
    upper_pipes = [
        {'x': SCREENWIDTH + 200, 'y': new_pipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': new_pipe2[0]['y']},
    ]
    # my List of lower pipes
    lower_pipes = [
        {'x': SCREENWIDTH + 200, 'y': new_pipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': new_pipe2[1]['y']},
    ]

    pipe_vel_x = -4

    player_vel_y = -8
    player_max_vel_y = 10
    player_acc_y = 1

    player_flap_v = -8
    player_flapped = False  # if flapping

    while True:  # Game loop
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if (event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP)) or (
                    event.type == MOUSEBUTTONDOWN and event.button == 1):
                if player_y > 0:
                    player_vel_y = player_flap_v
                    player_flapped = True
                    GAME_SOUNDS['wing'].play()

        crash_test = if_collided(player_x, player_y, upper_pipes,
                                 lower_pipes)  # This function will return true if the player is crashed
        if crash_test:
            return

        # check for score
        player_mid_pos = player_x + GAME_SPRITES['player'].get_width() / 2
        for pipe in upper_pipes:
            pipe_mid_pos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width() / 2
            if pipe_mid_pos <= player_mid_pos < pipe_mid_pos + 4:
                score += 1
                # print(f"Your score is {score}")
                GAME_SOUNDS['point'].play()

        if player_vel_y < player_max_vel_y and not player_flapped:
            player_vel_y += player_acc_y

        if player_flapped:
            player_flapped = False
        player_height = GAME_SPRITES['player'].get_height()
        player_y = player_y + min(player_vel_y, GROUND_Y - player_y - player_height)

        # move pipes to the left
        for upperPipe, lowerPipe in zip(upper_pipes, lower_pipes):
            upperPipe['x'] += pipe_vel_x
            lowerPipe['x'] += pipe_vel_x

        # Add a new pipe when the first is about to cross the leftmost part of the screen
        if 0 < upper_pipes[0]['x'] < 5:
            new_pipe = get_random_pipe()
            upper_pipes.append(new_pipe[0])
            lower_pipes.append(new_pipe[1])

        # if the pipe is out of the screen, remove it
        if upper_pipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upper_pipes.pop(0)
            lower_pipes.pop(0)

        # Lets blit our sprites now
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upper_pipes, lower_pipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (base_x, GROUND_Y))
        SCREEN.blit(GAME_SPRITES['player'], (player_x, player_y))
        my_digits = [int(x) for x in list(str(score))]
        width = 0
        for digit in my_digits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        x_offset = (SCREENWIDTH - width) / 2

        for digit in my_digits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (x_offset, SCREENHEIGHT * 0.12))
            x_offset += GAME_SPRITES['numbers'][digit].get_width()
        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def if_collided(player_x, player_y, upper_pipes, lower_pipes):
    if player_y >= GROUND_Y - GAME_SPRITES['player'].get_height() or player_y < 0:
        GAME_SOUNDS['hit'].play()
        return True

    for pipe in upper_pipes:
        pipe_height = GAME_SPRITES['pipe'][0].get_height()
        if player_y < pipe_height + pipe['y'] and abs(player_x - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lower_pipes:
        if (player_y + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(player_x - pipe['x']) < \
                GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True

    return False


def get_random_pipe():
    """
    Generate positions of two pipes(one bottom straight and one top rotated ) for blitting on the screen
    """
    pipe_height = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT / 3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - offset))
    pipe_x = SCREENWIDTH + 10
    y1 = pipe_height - y2 + offset
    pipe = [
        {'x': pipe_x, 'y': -y1},  # upper Pipe
        {'x': pipe_x, 'y': y2}  # lower Pipe
    ]
    return pipe


if __name__ == "__main__":
    # This will be the main point from where our game will start
    pygame.init()  # Initialize all pygame modules
    FPS_CLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird Game')
    GAME_SPRITES['numbers'] = (
        pygame.image.load('gallery/sprites/0.png').convert_alpha(),
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),
        pygame.image.load('gallery/sprites/9.png').convert_alpha(),
    )

    GAME_SPRITES['message'] = pygame.image.load('gallery/sprites/message.png').convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load('gallery/sprites/base.png').convert_alpha()
    GAME_SPRITES['pipe'] = (pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
                            pygame.image.load(PIPE).convert_alpha()
                            )

    # Game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')

    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()

    while True:
        welcome_screen()  # Shows welcome screen to the user until further input
        main_game()  # This is the main game function
