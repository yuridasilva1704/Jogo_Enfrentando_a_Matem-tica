# -*- coding: utf-8 -*-
import pgzrun
import random
from pygame import Rect

WIDTH = 700
HEIGHT = 400

TILE_SIZE = 43
TILE_COLS = WIDTH // TILE_SIZE
TILE_ROWS = HEIGHT // TILE_SIZE

WIN_SCORE = 50

game_state = 'menu'
sound_on = True

background_tile = 'fundo_jogo'

player_images = ['jogador_parado1', 'jogador_parado2', 'jogador_cima1', 'jogador_cima2',
                 'jogador_baixo1', 'jogador_baixo2', 'jogador_esquerda1', 'jogador_esquerda2',
                 'jogador_direita1', 'jogador_direita2']    
player = Actor('jogador_parado1')
player.grid_x = TILE_COLS // 2
player.grid_y = TILE_ROWS // 2
player.x = player.grid_x * TILE_SIZE + TILE_SIZE // 2
player.y = player.grid_y * TILE_SIZE + TILE_SIZE // 2

player.animation_frame = 0
player.moving = False
player.dx = 0
player.dy = 0
player.progress = 0.0
player.animation_timer = 0

enemy_images = ['inimigo1']
enemy = Actor('inimigo1')
enemy.grid_x = random.randint(0, TILE_COLS - 1)
enemy.grid_y = random.randint(0, TILE_ROWS - 1)
enemy.x = enemy.grid_x * TILE_SIZE + TILE_SIZE // 2
enemy.y = enemy.grid_y * TILE_SIZE + TILE_SIZE // 2

enemy.animation_frame = 0
enemy.animation_timer = 0

music.set_volume(1.0)
music.play('musica')

show_question = False
num1 = 0
num2 = 0
operation = '+'
feedback = ""
question_counter = 0
MAX_QUESTIONS = 5
player_score = 0
player_lives = 3

options = ['A', 'B', 'C', 'D', 'E']
correct_answer = ''
choices = []
choice_areas = []

operations_list = ['+', '-', '*', '/']

def draw():
    screen.clear()
    if game_state == 'menu':
        draw_menu()
    elif game_state == 'playing':
        if show_question:
            draw_question()
        else:
            draw_game()
    elif game_state == 'game_over':
        draw_game_over()
    elif game_state == 'victory':
        draw_victory()

def update(dt):
    animate_player(dt)

def animate_player(dt):
    if player.moving:
        player.progress += dt * 3 
        if player.progress >= 1:
            player.grid_x += player.dx
            player.grid_y += player.dy
            player.moving = False
            player.dx = 0
            player.dy = 0
        player.x = lerp(player.x, player.grid_x * TILE_SIZE + TILE_SIZE // 2, player.progress)
        player.y = lerp(player.y, player.grid_y * TILE_SIZE + TILE_SIZE // 2, player.progress)

    player.animation_timer += dt
    if player.animation_timer > 0.5:
        player.image = player_images[int(player.animation_frame % 2)]
        player.animation_frame += 0.5
        player.animation_timer = 0

def lerp(a, b, t):
    return a + (b - a) * t

def draw_button_rect(rect_values, text, font_size, bg_color):
    x, y, w, h = rect_values
    r = 10
    screen.draw.filled_rect(Rect((x + r, y), (w - 2 * r, h)), bg_color)
    screen.draw.filled_rect(Rect((x, y + r), (w, h - 2 * r)), bg_color)
    screen.draw.filled_circle((x + r, y + r), r, bg_color)
    screen.draw.filled_circle((x + w - r, y + r), r, bg_color)
    screen.draw.filled_circle((x + r, y + h - r), r, bg_color)
    screen.draw.filled_circle((x + w - r, y + h - r), r, bg_color)
    screen.draw.text(text, center=(x + w // 2, y + h // 2), fontsize=font_size, color="white")

def draw_menu():
    screen.blit('background_menu', (0, 0))
    draw_button_rect((225, 200, 250, 50), "Clique para Iniciar", 36, (255, 190, 0))
    draw_button_rect((225, 270, 250, 40), f"Musica: {'ON' if sound_on else 'OFF'}", 30, (255, 128, 0))
    draw_button_rect((225, 330, 250, 40), "Sair", 30, (200, 0, 0))

def draw_game():
    for x in range(TILE_COLS):
        for y in range(TILE_ROWS):
            screen.blit(background_tile, (x * TILE_SIZE, y * TILE_SIZE))
    screen.draw.text(f"Objetivo: 50", (10, 10), fontsize=25, color="green")
    screen.draw.text(f"Pontos: {player_score}", (10, 40), fontsize=25, color="black")
    screen.draw.text(f"Vidas: {player_lives}", (10, 60), fontsize=25, color="red")
    player.draw()
    enemy.draw()

def generate_choices():
    global correct_answer, choices, choice_areas
    if operation == '+':
        correct = num1 + num2
    elif operation == '-':
        correct = num1 - num2
    elif operation == '*':
        correct = num1 * num2
    elif operation == '/':
        correct = num1 // num2
    choices = [correct]
    while len(choices) < 5:
        fake = correct + random.randint(-10, 10)
        if fake >= 0 and fake not in choices:
            choices.append(fake)
    random.shuffle(choices)
    correct_answer = options[choices.index(correct)]
    choice_areas = []
    for i, (letter, value) in enumerate(zip(options, choices)):
        x = 80 + i * 120
        y = HEIGHT // 2
        choice_areas.append((letter, Rect((x - 40, y - 30), (80, 60))))

def draw_question():
    screen.fill("lightblue")
    screen.draw.text(f"Hahaha... Eu sou seu inimigo\nVamos ver suas habilidades.\nQual a resposta?\n\n{num1} {operation} {num2}?\n", center=(WIDTH//2, HEIGHT//2 - 100), fontsize=40, color="black")
    for (letter, rect), value in zip(choice_areas, choices):
        screen.draw.filled_rect(rect, "white")
        screen.draw.rect(rect, "black")
        screen.draw.text(f"{letter}) {value}", center=rect.center, fontsize=30, color="black")
    if feedback:
        screen.draw.text(feedback, center=(WIDTH//2, HEIGHT//2 + 100), fontsize=40, color="green" if "Correta" in feedback else "red")

def draw_game_over():
    screen.draw.text("FIM DE JOGO\nVoce perdeu...hahaha!", center=(WIDTH//2, HEIGHT//2 - 30), fontsize=60, color="red")
    screen.draw.text(f"Pontuacao final: {player_score}", center=(WIDTH//2, HEIGHT//2 + 30), fontsize=40, color="white")
    draw_button_rect((WIDTH//2 - 100, HEIGHT//2 + 80, 200, 50), "Voltar ao Menu", 30, (0, 100, 200))

def draw_victory():
    screen.draw.text("VOCE VENCEU!\nFui derrotado, meus parabens!", center=(WIDTH//2, HEIGHT//2 - 30), fontsize=60, color="green")
    screen.draw.text(f"Pontuacao final: {player_score}", center=(WIDTH//2, HEIGHT//2 + 30), fontsize=40, color="white")
    draw_button_rect((WIDTH//2 - 100, HEIGHT//2 + 80, 200, 50), "Voltar ao Menu", 30, (0, 100, 200))

def on_mouse_down(pos):
    global game_state, sound_on, show_question, feedback, player_score, question_counter, player_lives
    x, y = pos
    if game_state == 'menu':
        if 225 <= x <= 475 and 200 <= y <= 250:
            game_state = 'playing'
        elif 225 <= x <= 475 and 270 <= y <= 310:
            sound_on = not sound_on
            if sound_on:
                music.play('musica')
            else:
                music.stop()
        elif 225 <= x <= 475 and 330 <= y <= 370:
            exit()
    elif game_state == 'playing' and show_question:
        for letter, rect in choice_areas:
            if rect.collidepoint(pos):
                if letter == correct_answer:
                    player_score += 10
                    feedback = "Resposta Correta!"
                else:
                    player_lives -= 1
                    feedback = "Errado!"
                question_counter += 1
                clock.schedule_unique(next_question_or_end, 2.0)
                break
    elif game_state in ['game_over', 'victory']:
        if WIDTH//2 - 100 <= x <= WIDTH//2 + 100 and HEIGHT//2 + 80 <= y <= HEIGHT//2 + 130:
            reset_game()

def on_key_down(key):
    global game_state
    if game_state in ['game_over', 'victory'] and key == keys.ESCAPE:
        reset_game()
    if game_state != 'playing' or show_question:
        return
    move_dir = None
    if key == keys.LEFT:
        move_dir = (-1, 0)
        player.image = player_images[6 + int(player.animation_frame % 2)] 
    elif key == keys.RIGHT:
        move_dir = (1, 0)
        player.image = player_images[8 + int(player.animation_frame % 2)]
    elif key == keys.UP:
        move_dir = (0, -1)
        player.image = player_images[2 + int(player.animation_frame % 2)] 
    elif key == keys.DOWN:
        move_dir = (0, 1)
        player.image = player_images[4 + int(player.animation_frame % 2)] 

    if move_dir:
        player.dx, player.dy = move_dir
        player.moving = True
        player.progress = 0.0
        check_collision()

def check_collision():
    global show_question, num1, num2, feedback, operation
    dx = abs(player.grid_x - enemy.grid_x)
    dy = abs(player.grid_y - enemy.grid_y)
    
    if dx <= 2 and dy <= 2:
        num1 = random.randint(1, 20)
        num2 = random.randint(1, 20)
        operation = random.choice(operations_list)
        if operation == '/':
            num1 = num1 * num2
        generate_choices()
        show_question = True
        feedback = ""

def next_question_or_end():
    global show_question, game_state
    if player_score >= WIN_SCORE:
        game_state = 'victory'
    elif player_lives <= 0:
        game_state = 'game_over'
    else:
        reset_enemy()
        show_question = False

def reset_enemy():
    enemy.grid_x = random.randint(0, TILE_COLS - 1)
    enemy.grid_y = random.randint(0, TILE_ROWS - 1)
    enemy.x = enemy.grid_x * TILE_SIZE + TILE_SIZE // 2
    enemy.y = enemy.grid_y * TILE_SIZE + TILE_SIZE // 2

def reset_game():
    global game_state, player_score, question_counter, player_lives
    game_state = 'menu'
    player_score = 0
    question_counter = 0
    player_lives = 3

pgzrun.go()