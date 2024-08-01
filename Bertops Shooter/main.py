import pygame
import random
import time
import math
import os

pygame.font.init()

WIDTH, HEIGHT = 1000, 700
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Bertops Shooter')

current_dir = os.path.dirname(__file__)
image_path = os.path.join(current_dir, 'bg.jpeg')
BG = pygame.image.load(image_path)

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60

PLAYER_VELOCITY = 5
STAR_WIDTH = 10
STAR_HEIGHT = 20
STAR_VELOCITY = 3
PROJECTILE_WIDTH = 5
PROJECTILE_HEIGHT = 10
PROJECTILE_VELOCITY = 5
RED_STAR_PROJECTILE_VELOCITY = 10
GREEN_STAR_HIT_COUNT = 2
BLUE_STAR_EXPLOSION_RADIUS = 50
ORANGE_STAR_EFFECT_RADIUS = WIDTH  # Yıldız ekranın tüm genişliğini kaplayabilir
EXPLOSION_DURATION = 1000  # 1 saniye (milisaniye cinsinden)

FONT = pygame.font.SysFont('comicsans', 30)

# Renkleri döndüren bir fonksiyon
def get_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

class Star(pygame.Rect):
    def __init__(self, x, y, width, height, color, is_shooting=False, hit_count=1):
        super().__init__(x, y, width, height)
        self.color = color
        self.is_shooting = is_shooting
        self.hit_count = hit_count

class Explosion:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.start_time = pygame.time.get_ticks()

    def draw(self):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time
        if elapsed_time < EXPLOSION_DURATION:
            pygame.draw.circle(WINDOW, "yellow", (self.x, self.y), self.radius, 1)

def draw(player, player_color, elapsed_time, stars, projectiles, red_star_projectiles, explosions):
    WINDOW.blit(BG, (0, 0))

    time_text = FONT.render(f'Time: {round(elapsed_time)}s', 1, 'white')
    WINDOW.blit(time_text, (10, 10))

    pygame.draw.rect(WINDOW, player_color, player)

    for star in stars:
        pygame.draw.rect(WINDOW, star.color, star)

    for projectile in projectiles:
        pygame.draw.rect(WINDOW, "blue", projectile)

    for red_projectile in red_star_projectiles:
        pygame.draw.rect(WINDOW, "orange", red_projectile)

    for explosion in explosions:
        explosion.draw()

    pygame.display.update()

def main_game():
    player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    player_color = get_random_color()  # Başlangıç rengi
    color_change_time = 500  # Milisaniye cinsinden renk değiştirme süresi
    last_color_change = pygame.time.get_ticks()  # Son renk değiştirme zamanı

    clock = pygame.time.Clock()

    start_time = time.time()
    elapsed_time = 0

    star_add_increment = 2000
    star_count = 0

    stars = []
    projectiles = []
    red_star_projectiles = []  # Kırmızı yıldız projeksiyonları için liste
    explosions = []  # Patlamalar için liste
    hit = False
    star_hits = 0
    paused = False  # Oyun duraklatma durumu

    run = True
    while run:
        star_count += clock.tick(100)
        elapsed_time = time.time() - start_time

        current_time = pygame.time.get_ticks()
        if current_time - last_color_change > color_change_time:
            player_color = get_random_color()
            last_color_change = current_time

        if star_count > star_add_increment:
            for _ in range(3):
                star_x = random.randint(0, WIDTH - STAR_WIDTH)
                star_color = random.choices(["white", "red", "green", "blue", "orange"], [0.65, 0.2, 0.1, 0.025, 0.025])[0]
                star_is_shooting = star_color == "red"
                star_hit_count = GREEN_STAR_HIT_COUNT if star_color == "green" else 1
                star = Star(star_x, -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT, star_color, star_is_shooting, star_hit_count)
                stars.append(star)
            star_add_increment = max(200, star_add_increment - 50)
            star_count = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, elapsed_time, star_hits
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    projectile = pygame.Rect(player.x + player.width / 2, player.y, PROJECTILE_WIDTH, PROJECTILE_HEIGHT)
                    projectiles.append(projectile)
                if event.key == pygame.K_p:
                    paused = not paused  # Oyun duraklatma

        if not paused:
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player.x - PLAYER_VELOCITY >= 0:
                player.x -= PLAYER_VELOCITY
            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player.x + PLAYER_VELOCITY + player.width <= WIDTH:
                player.x += PLAYER_VELOCITY

            for star in stars[:]:
                star.y += STAR_VELOCITY
                if star.y > HEIGHT:
                    stars.remove(star)
                elif star.y + star.height >= player.y and star.colliderect(player):
                    stars.remove(star)
                    hit = True
                    break

            for projectile in projectiles[:]:
                projectile.y -= PROJECTILE_VELOCITY
                if projectile.y < 0:
                    projectiles.remove(projectile)
                else:
                    for star in stars[:]:
                        if projectile.colliderect(star):
                            projectiles.remove(projectile)
                            star.hit_count -= 1
                            if star.hit_count <= 0:
                                if star.color == "blue":
                                    # Mavi yıldız patlaması
                                    explosion = Explosion(star.x + star.width / 2, star.y + star.height / 2, BLUE_STAR_EXPLOSION_RADIUS)
                                    explosions.append(explosion)
                                    stars = [s for s in stars if not (math.hypot(s.x - star.x, s.y - star.y) <= BLUE_STAR_EXPLOSION_RADIUS and s.color != "green")]
                                elif star.color == "orange":
                                    # Turuncu yıldız etkisi
                                    stars.clear()
                                else:
                                    stars.remove(star)
                            star_hits += 1
                            break

            for star in stars[:]:
                if star.color == "red" and star.is_shooting:
                    projectile = pygame.Rect(star.x + star.width / 2 - PROJECTILE_WIDTH / 2, star.y + star.height, PROJECTILE_WIDTH, PROJECTILE_HEIGHT)
                    red_star_projectiles.append(projectile)
                    star.is_shooting = False

            for projectile in red_star_projectiles[:]:
                projectile.y += RED_STAR_PROJECTILE_VELOCITY
                if projectile.y > HEIGHT:
                    red_star_projectiles.remove(projectile)
                elif projectile.colliderect(player):
                    hit = True
                    break

            # Patlamaları güncelle
            explosions = [explosion for explosion in explosions if pygame.time.get_ticks() - explosion.start_time < EXPLOSION_DURATION]

            if hit:
                lost_text = FONT.render("You Lost!", 1, "white")
                WINDOW.blit(lost_text, (WIDTH / 2 - lost_text.get_width() / 2, HEIGHT / 2 - lost_text.get_height() / 2))
                pygame.display.update()
                pygame.time.delay(2000)
                return False, elapsed_time, star_hits

        draw(player, player_color, elapsed_time, stars, projectiles, red_star_projectiles, explosions)

    return True, elapsed_time, star_hits

def draw_menu():
    WINDOW.fill((0, 0, 0))
    title_text = FONT.render("Bertops Shooter", 1, "white")
    start_text = FONT.render("Press ENTER to Start", 1, "white")
    exit_text = FONT.render("Press ESC to Exit", 1, "white")
    WINDOW.blit(title_text, (WIDTH / 2 - title_text.get_width() / 2, HEIGHT / 2 - title_text.get_height() / 2 - 40))
    WINDOW.blit(start_text, (WIDTH / 2 - start_text.get_width() / 2, HEIGHT / 2 - start_text.get_height() / 2))
    WINDOW.blit(exit_text, (WIDTH / 2 - exit_text.get_width() / 2, HEIGHT / 2 - exit_text.get_height() / 2 + 40))
    pygame.display.update()

def main_menu():
    while True:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    run_game = True
                    while run_game:
                        run_game, elapsed_time, star_hits = main_game()
                        if not run_game:
                            lost_screen(elapsed_time, star_hits)
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

def lost_screen(elapsed_time, star_hits):
    while True:
        WINDOW.fill((0, 0, 0))
        lost_text = FONT.render("You Lost!", 1, "white")
        time_text = FONT.render(f"Time: {round(elapsed_time)}s", 1, "white")
        star_hits_text = FONT.render(f"Stars Hit: {star_hits}", 1, "white")
        retry_text = FONT.render("Press ENTER to Try Again", 1, "white")
        exit_text = FONT.render("Press ESC to Exit", 1, "white")
        WINDOW.blit(lost_text, (WIDTH / 2 - lost_text.get_width() / 2, HEIGHT / 2 - lost_text.get_height() / 2 - 40))
        WINDOW.blit(time_text, (WIDTH / 2 - time_text.get_width() / 2, HEIGHT / 2 - time_text.get_height() / 2))
        WINDOW.blit(star_hits_text, (WIDTH / 2 - star_hits_text.get_width() / 2, HEIGHT / 2 - star_hits_text.get_height() / 2 + 40))
        WINDOW.blit(retry_text, (WIDTH / 2 - retry_text.get_width() / 2, HEIGHT / 2 - retry_text.get_height() / 2 + 80))
        WINDOW.blit(exit_text, (WIDTH / 2 - exit_text.get_width() / 2, HEIGHT / 2 - exit_text.get_height() / 2 + 120))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

if __name__ == "__main__":
    main_menu()
