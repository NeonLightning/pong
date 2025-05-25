import math
import struct
import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
import pygame.mixer
import random
import argparse

parser = argparse.ArgumentParser(description="Pong Game")
parser.add_argument("-p", "--points", type=int, default=10, help="Maximum score points for game over (default is 10)")
parser.add_argument("-b", "--brain", type=int, default=5, help="AI difficulty level between 1-10 (default is 5)")
parser.add_argument("-i", "--increase", type=int, default=2, help="Speed Increase(default is 2)")
parser.add_argument("--colored", action="store_true", help="Adds colors")
parser.add_argument("--mouse", action="store_true", help="Control paddle with mouse instead of arrow keys")
parser.add_argument("--mute", action="store_true", help="Mute all in-game sounds")
args = parser.parse_args()
pygame.mixer.init()
pygame.init()
pygame.joystick.init()
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
screen_info = pygame.display.Info()
screen_width, screen_height = screen_info.current_w, screen_info.current_h
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
paddle_width = int(screen_width * 0.01)
paddle_height = int(screen_height * 0.15)
ball_size = int(min(screen_width, screen_height) * 0.02)
player_paddle = pygame.Rect(screen_width - paddle_width - 20, (screen_height - paddle_height) / 2, paddle_width, paddle_height)
player_paddle_color = WHITE
opponent_paddle = pygame.Rect(20, (screen_height - paddle_height) / 2, paddle_width, paddle_height)
opponent_paddle_color = WHITE
bg_color = WHITE
player_score = 0
opponent_score = 0
font = pygame.font.Font(None, 74)

def random_8bit_color():
    if args.colored:
        while True:
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            return (r, g, b)
    else:
        return (255, 255, 255)

def play_ping1_sound():
    if args.mute:
        return
    frequency = 150
    duration = 100
    volume = 0.5
    sound = pygame.mixer.Sound(gen_ping_sound(frequency, duration))
    sound.set_volume(volume)
    sound.play()
    
def play_ping2_sound():
    if args.mute:
        return
    frequency = 210
    duration = 100
    volume = 0.5
    sound = pygame.mixer.Sound(gen_ping_sound(frequency, duration))
    sound.set_volume(volume)
    sound.play()

def play_score_sound():
    if args.mute:
        return
    frequency = 380
    duration = 200
    volume = 0.7
    sound = pygame.mixer.Sound(gen_ping_sound(frequency, duration))
    sound.set_volume(volume)
    sound.play()

def gen_ping_sound(freq, ms):
    if args.mute:
        return
    sample_rate = pygame.mixer.get_init()[0]
    samples = int(sample_rate * (ms / 1000.0))
    buffer = bytes()
    for i in range(samples):
        s = math.sin(2*math.pi*i*freq/sample_rate)
        buffer += struct.pack('B', int((s+1)*127.5))
    return buffer

def display_scores():
    player_text = font.render(str(player_score), True, bg_color)
    opponent_text = font.render(str(opponent_score), True, bg_color)
    spacing = 40
    player_x_pos = (screen_width // 2) + spacing
    opponent_x_pos = (screen_width // 2) - opponent_text.get_width() - spacing
    screen.blit(player_text, (player_x_pos, 50))
    screen.blit(opponent_text, (opponent_x_pos, 50))

def show_game_over():
    start_timer = pygame.time.get_ticks()
    while (pygame.time.get_ticks() - start_timer) < 5000:
        screen.fill(BLACK) 
        game_over_text_color = random_8bit_color()
        game_over_text = font.render("Game Over", True, game_over_text_color)
        player_wins_text = font.render(f"Player Wins: {player_score}", True, game_over_text_color)
        opponent_wins_text = font.render(f"Opponent Wins: {opponent_score}", True, game_over_text_color)
        screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 3))
        screen.blit(player_wins_text, (screen_width // 2 - player_wins_text.get_width() // 2, screen_height // 2))
        screen.blit(opponent_wins_text, (screen_width // 2 - opponent_wins_text.get_width() // 2, screen_height * 2 // 3))
        pygame.display.flip()
        pygame.time.wait(50)

def show_pause_screen():
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.fill((0, 0, 0))
    pause_text = font.render("Paused: Escape or Button 6 to quit", True, (255, 255, 255))
    text_rect = pause_text.get_rect(center=(screen_width // 2, screen_height // 2))
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    paused = False
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 6:
                    pygame.quit()
                    sys.exit()
                elif event.button == 7:
                    paused= False
        screen.blit(overlay, (0, 0))
        screen.blit(pause_text, text_rect)
        pygame.display.flip()
        clock.tick(15)
        
base_speed_factor = min(screen_width, screen_height) * 0.0115
ball_speed_x = base_speed_factor
ball_speed_y = base_speed_factor
player_speed = base_speed_factor + 8
ball = pygame.Rect((screen_width - ball_size) // 2, screen_height // 2, ball_size, ball_size)
ball_speed_increase_factor = args.increase
running = True
clock = pygame.time.Clock()
frame_counter = 0
ball_color = random_8bit_color()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                show_pause_screen()
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 7:
                show_pause_screen()
            elif event.button == 6:
                pygame.quit()
                sys.exit()
    if args.mouse:
        mouse_y = pygame.mouse.get_pos()[1]
        player_paddle.centery = mouse_y
        if player_paddle.top < 0:
            player_paddle.top = 0
        if player_paddle.bottom > screen_height:
            player_paddle.bottom = screen_height
    else:
        moved = False
        if joystick:
            axis_value = joystick.get_axis(1)
            if abs(axis_value) > 0.1:
                player_paddle.y += axis_value * player_speed
                moved = True
            hat = joystick.get_hat(0)
            if hat[1] == 1 and player_paddle.top > 0:
                player_paddle.y -= player_speed
                moved = True
            elif hat[1] == -1 and player_paddle.bottom < screen_height:
                player_paddle.y += player_speed
                moved = True
        if not moved:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and player_paddle.top > 0:
                player_paddle.y -= player_speed
            if keys[pygame.K_DOWN] and player_paddle.bottom < screen_height:
                player_paddle.y += player_speed
    ai_random_factor = random.random()
    if ai_random_factor < (args.brain / 10.0):
        target_y = ball.centery
        overshoot_range = paddle_height * 0.15
        if random.random() < 0.5:
            target_y += random.uniform(0, overshoot_range)
        else:
            target_y -= random.uniform(0, overshoot_range)
        if opponent_paddle.centery < target_y:
            move_amount = min(player_speed, target_y - opponent_paddle.centery)
            opponent_paddle.y += move_amount
        elif opponent_paddle.centery > target_y:
            move_amount = min(player_speed, opponent_paddle.centery - target_y)
            opponent_paddle.y -= move_amount
    opponent_paddle.top = max(0, opponent_paddle.top)
    opponent_paddle.bottom = min(screen_height, opponent_paddle.bottom)
    frame_counter += 1
    if frame_counter > 20:
        ball_color = random_8bit_color()
        if ball_color == (0, 0, 0):
            ball_color = random_8bit_color()
        frame_counter = 0
    if ball.top <= 0 or ball.bottom >= screen_height:
        ball_speed_y *= -1
    if ball.left <= 0:
        player_score += 1
        ball.center = (screen_width // 2, screen_height // 2)
        ball_speed_x = base_speed_factor
        play_score_sound()
    if ball.right >= screen_width:
        opponent_score += 1
        ball.center = (screen_width // 2, screen_height // 2)
        bg_color = random_8bit_color()
        if bg_color == (0, 0, 0):
            bg_color = random_8bit_color()
        ball_speed_x = -base_speed_factor
        play_score_sound()
    if player_score >= args.points or opponent_score >= args.points:
        show_game_over()
        running = False
    next_ball_x = ball.x + ball_speed_x
    next_ball_y = ball.y + ball_speed_y
    current_ball_x = ball.x
    if ball_speed_x > 0:
        if (ball.right <= player_paddle.left and next_ball_x + ball_size > player_paddle.left) or \
           (ball.right > player_paddle.left and next_ball_x + ball_size >= player_paddle.left):
            if ball.bottom > player_paddle.top and ball.top < player_paddle.bottom:
                ball.right = player_paddle.left
                ball_speed_x = -(abs(ball_speed_x) + ball_speed_increase_factor)
                player_paddle_color = random_8bit_color()
                if player_paddle_color == (0, 0, 0):
                    player_paddle_color = random_8bit_color()
                play_ping1_sound()
                next_ball_x = ball.x + ball_speed_x
    elif ball_speed_x < 0:
        if (ball.left >= opponent_paddle.right and next_ball_x < opponent_paddle.right) or \
           (ball.left < opponent_paddle.right and next_ball_x <= opponent_paddle.right):
            if ball.bottom > opponent_paddle.top and ball.top < opponent_paddle.bottom:
                ball.left = opponent_paddle.right
                ball_speed_x = (abs(ball_speed_x) + ball_speed_increase_factor)
                opponent_paddle_color = random_8bit_color()
                if opponent_paddle_color == (0, 0, 0):
                    opponent_paddle_color = random_8bit_color()
                play_ping2_sound()
                next_ball_x = ball.x + ball_speed_x
    ball.x = next_ball_x
    ball.y += ball_speed_y
    screen.fill(BLACK)
    pygame.draw.rect(screen, player_paddle_color, player_paddle)
    pygame.draw.rect(screen, opponent_paddle_color, opponent_paddle)
    pygame.draw.ellipse(screen, ball_color, ball)
    line_width = 20
    center_x = screen_width // 2
    line_rect = pygame.Rect(center_x - (line_width // 2), 0, line_width, screen_height)
    pygame.draw.rect(screen, bg_color, line_rect)
    display_scores()
    pygame.display.flip()
    clock.tick(60)
pygame.quit()