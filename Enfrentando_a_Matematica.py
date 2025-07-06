import pgzrun
import random
from pygame import Rect

WIDTH = 700
HEIGHT = 400

TILE_SIZE = 43
TILE_COLS = WIDTH // TILE_SIZE
TILE_ROWS = HEIGHT // TILE_SIZE
WIN_SCORE = 100

game_state = 'menu'
sound_on = True
show_instructions = False

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
player.can_attack = True
player.attacking = False

class Enemy:
    def __init__(self):
        self.actor = Actor('inimigo1')
        self.respawn()

    def respawn(self):
        while True:
            self.grid_x = random.randint(0, TILE_COLS - 1)
            self.grid_y = random.randint(0, TILE_ROWS - 1)
            if abs(self.grid_x - player.grid_x) >= 3 and abs(self.grid_y - player.grid_y) >= 3:
                break
        self.actor.x = self.grid_x * TILE_SIZE + TILE_SIZE // 2
        self.actor.y = self.grid_y * TILE_SIZE + TILE_SIZE // 2
        self.health = 2
        self.moving = False
        self.progress = 0.0
        self.dx = 0
        self.dy = 0
        self.cooldown = 0

    def update(self, dt):
        if self.health <= 0:
            return
        self.cooldown -= dt
        if not self.moving and self.cooldown <= 0:
            dx = player.grid_x - self.grid_x
            dy = player.grid_y - self.grid_y
            if abs(dx) > abs(dy):
                self.dx = 1 if dx > 0 else -1
                self.dy = 0
            else:
                self.dx = 0
                self.dy = 1 if dy > 0 else -1
            new_x = self.grid_x + self.dx
            new_y = self.grid_y + self.dy
            if 0 <= new_x < TILE_COLS and 0 <= new_y < TILE_ROWS:
                self.moving = True
                self.progress = 0.0
                self.cooldown = 1
        if self.moving:
            self.progress += dt * 3
            if self.progress >= 1:
                self.grid_x += self.dx
                self.grid_y += self.dy
                self.moving = False
                self.dx = self.dy = 0
            self.actor.x = lerp(self.actor.x, self.grid_x * TILE_SIZE + TILE_SIZE // 2, self.progress)
            self.actor.y = lerp(self.actor.y, self.grid_y * TILE_SIZE + TILE_SIZE // 2, self.progress)

enemies = [Enemy()]

music.set_volume(1.0)
music.play('musica')

show_question = False
question_enemy = None
num1 = 0
num2 = 0
operation = '+'
feedback = ""
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
    elif game_state == 'instructions':
        draw_instructions()
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
    for e in enemies:
        e.update(dt)
    if not show_question:
        check_collision()
    check_combat()

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
        if player.attacking:
            player.image = 'ataque'
        else:
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
    draw_button_rect((225, 175, 250, 50), "Clique para Iniciar", 36, (255, 190, 0))
    draw_button_rect((225, 230, 250, 40), "Regras", 30, (0, 120, 255))
    draw_button_rect((225, 280, 250, 40), f"Musica: {'ON' if sound_on else 'OFF'}", 30, (255, 128, 0))
    draw_button_rect((225, 330, 250, 40), "Sair", 30, (200, 0, 0))

def draw_instructions():
    screen.fill("lightblue")
    instrucoes = [
        "Regras:",
        "- Use as setas para se mover.",
        "- Pressione ESPACO para atacar.",
        "- Derrote inimigos para ganhar 10 pontos.",
        "- Se atacar e eliminar um inimigo (tecla espaco), ele se multiplica!",
        "- Se encostar no inimigo, responda a pergunta.",
        "- Acertando a pergunta: +5 pontos.",
        "- Errando: -10 pontos (se chegar a 0, perde uma vida).",
        "Chegue a 100 pontos para vencer!"
    ]
    y = 40
    for linha in instrucoes:
        screen.draw.text(linha, center=(WIDTH // 2, y), fontsize=30, color="black")
        y += 35
    draw_button_rect((WIDTH//2 - 100, 360, 200, 40), "Voltar ao Menu", 28, (0, 100, 200))


def draw_game():
    for x in range(TILE_COLS):
        for y in range(TILE_ROWS):
            screen.blit(background_tile, (x * TILE_SIZE, y * TILE_SIZE))
    screen.draw.text(f"Pontos: {player_score}", (10, 10), fontsize=30, color="black")
    screen.draw.text(f"Vidas: {player_lives}", (10, 50), fontsize=30, color="red")
    player.draw()
    for e in enemies:
        if e.health > 0:
            e.actor.draw()

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
    screen.draw.text(f"Hahaha... Qual a resposta?\n\n{num1} {operation} {num2}?\n", center=(WIDTH//2, HEIGHT//2 - 100), fontsize=40, color="black")
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
    global game_state, sound_on, show_question, feedback, player_score, player_lives, enemies
    x, y = pos
    if game_state == 'menu':
        if 225 <= x <= 475 and 160 <= y <= 210:
            game_state = 'playing'
        elif 225 <= x <= 475 and 230 <= y <= 270:
            game_state = 'instructions'
        elif 225 <= x <= 475 and 280 <= y <= 320:
            sound_on = not sound_on
            if sound_on:
                music.play('musica')
            else:
                music.stop()
        elif 225 <= x <= 475 and 330 <= y <= 370:
            exit()
    elif game_state == 'instructions':
        if WIDTH//2 - 100 <= x <= WIDTH//2 + 100 and 360 <= y <= 400:
            game_state = 'menu'
    elif game_state == 'playing' and show_question:
        for letter, rect in choice_areas:
            if rect.collidepoint(pos):
                if letter == correct_answer:
                    feedback = "Resposta Correta!"
                    player_score += 5
                else:
                    feedback = "Errado!"
                    player_score -= 10
                    if player_score <= 0:
                        player_score = 0
                        player_lives -= 1
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
    elif key == keys.SPACE and player.can_attack:
        player.attacking = True
        attack_enemy()
        player.can_attack = False
        clock.schedule_unique(enable_attack, 0.5)
        clock.schedule_unique(disable_attack_sprite, 0.3)
    if move_dir:
        player.dx, player.dy = move_dir
        player.moving = True
        player.progress = 0.0

def enable_attack():
    player.can_attack = True

def disable_attack_sprite():
    player.attacking = False

def check_collision():
    global show_question, num1, num2, feedback, operation, question_enemy
    if show_question:
        return
    for e in enemies:
        if e.health > 0 and player.grid_x == e.grid_x and player.grid_y == e.grid_y:
            num1 = random.randint(1, 20)
            num2 = random.randint(1, 20)
            operation = random.choice(operations_list)
            if operation == '/':
                num1 *= num2
            generate_choices()
            show_question = True
            feedback = ""
            question_enemy = e
            break

def attack_enemy():
    global player_score, enemies
    for e in enemies[:]:
        if e.health <= 0:
            continue
        if abs(player.grid_x - e.grid_x) <= 1 and abs(player.grid_y - e.grid_y) <= 1:
            e.health -= 1
            if e.health <= 0:
                player_score += 10
                enemies.remove(e)
                enemies.append(Enemy())
                enemies.append(Enemy())

def check_combat():
    global game_state
    if player_lives <= 0:
        game_state = 'game_over'
    if player_score >= WIN_SCORE:
        game_state = 'victory'

def next_question_or_end():
    global show_question, enemies
    show_question = False
    enemies = [Enemy()]

def reset_game():
    global game_state, player_score, player_lives, show_question, enemies
    game_state = 'menu'
    player_score = 0
    player_lives = 3
    show_question = False
    enemies = [Enemy()]

pgzrun.go()
