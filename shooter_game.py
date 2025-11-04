from pygame import *
from random import randint

# Инициализация шрифтов
font.init()

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, player_speed, width=65, height=65):
        super().__init__()
        self.image = transform.scale(image.load(player_image), (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
        self.speed = player_speed
    
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        # Управление стрелками
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < 700 - 80:
            self.rect.x += self.speed
        # Управление клавишами A и D
        if keys[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x < 700 - 80:
            self.rect.x += self.speed
    
    def fire(self):
        bullet = Bullet("bullet.png", self.rect.centerx - 7, self.rect.top, 10, 15, 20)
        bullets.add(bullet)
    
    def fire_piercing(self):
        piercing_bullet = PiercingBullet("bullet.png", self.rect.centerx - 7, self.rect.top, 15, 25, 30)
        piercing_bullets.add(piercing_bullet)

class Enemy(GameSprite):
    def update(self):
        # Враги не двигаются, если на карте есть босс
        if boss is 'Arial':
            self.rect.y += self.speed
            if self.rect.y > 500:
                self.rect.y = 0
                self.rect.x = randint(50, 650)
                global missed_enemies
                missed_enemies += 1

class Boss(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed, width=350, height=250):
        super().__init__(player_image, player_x, player_y, player_speed, width, height)
        self.health = 10
        self.max_health = 10
    
    def update(self):
        # Медленное движение вниз
        self.rect.y += self.speed
    
    def reset(self):
        super().reset()
        # Отрисовка полоски здоровья
        health_width = 200
        health_height = 15
        health_x = self.rect.centerx - health_width // 2
        health_y = self.rect.y - 25
        
        # Фон полоски здоровья
        draw.rect(window, (255, 0, 0), (health_x, health_y, health_width, health_height))
        # Текущее здоровье
        current_health_width = (self.health / self.max_health) * health_width
        draw.rect(window, (0, 255, 0), (health_x, health_y, current_health_width, health_height))

class Bullet(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed, width, height):
        super().__init__(player_image, player_x, player_y, player_speed, width, height)
    
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()

class PiercingBullet(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed, width, height):
        super().__init__(player_image, player_x, player_y, player_speed, width, height)
        self.damage = 3  # Пробивная пуля наносит урон всем врагам на пути
    
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()

# Создание окна игры
window = display.set_mode((700, 500))
display.set_caption("Расстрел Дроздов")

# Загрузка фонов
normal_background = transform.scale(image.load("galaxy.jpg"), (700, 500))
endless_background = transform.scale(image.load("galaxy2.jpeg"), (700, 500))

# Создание игрока
player = Player('rocket.png', 300, 430, 5, 80, 100)

# Создание врагов
enemies = sprite.Group()
for i in range(5):
    enemy = Enemy("oreshnik.png", randint(50, 650), -50, randint(1, 3), 80, 50)
    enemies.add(enemy)

# Создание группы для пуль
bullets = sprite.Group()
piercing_bullets = sprite.Group()  # Группа для пробивных пуль

# Босс
boss = 'Arial'
boss_spawn_kills = 50  # Босс появляется после 50 убитых врагов
bosses_killed = 0  # Счетчик убитых боссов
last_boss_spawn = 0  # Счетчик врагов при последнем появлении босса

# Счетчики
score = 0
missed_enemies = 0
goal = 10  # Цель - убить 10 врагов
high_score = 0  # Рекорд в бесконечном режиме
enemies_killed = 0  # Счетчик убитых врагов

# Перезарядка пробивного выстрела
piercing_cooldown = 0  # Текущее время перезарядки
piercing_max_cooldown = 900  # 15 секунд (60 FPS * 15 = 900 кадров)
piercing_ready = True  # Готов ли пробивной выстрел

# Шрифты
font1 = font.SysFont('Arial', 36)
font2 = font.SysFont('Arial', 80)

# Текст победы и поражения
win_text = font2.render("YOU WIN!", True, (0, 255, 0))
lose_text = font2.render("YOU LOSE!", True, (255, 0, 0))

# Музыка
mixer.init()
mixer.music.load("space.ogg")
mixer.music.play(-1)  # -1 означает бесконечное повторение
fire_sound = mixer.Sound("fire.ogg")
music_playing = True  # Флаг для отслеживания состояния музыки

# Бесконечный режим
endless_mode = False
game = True
finish = False
clock = time.Clock()
FPS = 60

def reset_game():
    global score, missed_enemies, finish, boss, enemies_killed, bosses_killed, last_boss_spawn
    global piercing_cooldown, piercing_ready
    score = 0
    missed_enemies = 0
    enemies_killed = 0
    bosses_killed = 0
    last_boss_spawn = 0
    piercing_cooldown = 0
    piercing_ready = True
    finish = False
    boss = 'Arial'
    
    # Очистка всех врагов
    enemies.empty()
    
    # Создание новых врагов
    for i in range(5):
        enemy = Enemy("oreshnik.png", randint(50, 650), -50, randint(1, 3), 80, 50)
        enemies.add(enemy)
    
    # Очистка пуль
    bullets.empty()
    piercing_bullets.empty()
    
    # Сброс позиции игрока
    player.rect.x = 300

def spawn_boss():
    global boss, last_boss_spawn
    # Босс появляется сверху по центру, размером с пол карты (350x250), скорость 1 (в 5 раз медленнее)
    boss = Boss("oreshnik.png", 175, -250, 1, 350, 250)
    last_boss_spawn = enemies_killed  # Запоминаем, при каком счетчике появился босс

while game:
    for e in event.get():
        if e.type == QUIT:
            game = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE and not finish:
                player.fire()
                fire_sound.play()
            if e.key == K_q and not finish and piercing_ready:
                player.fire_piercing()
                fire_sound.play()
                piercing_ready = False
                piercing_cooldown = piercing_max_cooldown
            if e.key == K_r and finish:
                reset_game()
                
            # Выключение/включение музыки при нажатии T
            if e.key == K_t:
                if music_playing:
                    mixer.music.pause()
                    music_playing = False
                else:
                    mixer.music.unpause()
                    music_playing = True
            
            # Включение/выключение бесконечного режима при нажатии G
            if e.key == K_g and finish:
                endless_mode = not endless_mode
                reset_game()

    if not finish:
        # Обновление перезарядки пробивного выстрела
        if not piercing_ready:
            piercing_cooldown -= 1
            if piercing_cooldown <= 0:
                piercing_ready = True
                piercing_cooldown = 0
        
        # Выбор фона в зависимости от режима
        if endless_mode:
            window.blit(endless_background, (0, 0))
        else:
            window.blit(normal_background, (0, 0))
        
        # Обновление и отрисовка игрока
        player.update()
        player.reset()
        
        # Обновление и отрисовка врагов (только если нет босса)
        if boss is 'Arial':
            enemies.update()
        enemies.draw(window)
        
        # Обновление и отрисовка обычных пуль
        bullets.update()
        bullets.draw(window)
        
        # Обновление и отрисовка пробивных пуль
        piercing_bullets.update()
        piercing_bullets.draw(window)
        
        # В бесконечном режиме проверяем появление босса (после каждых 50 убитых врагов)
        if endless_mode and boss is 'Arial' and enemies_killed >= last_boss_spawn + boss_spawn_kills:
            spawn_boss()
        
        # Обновление и отрисовка босса
        if endless_mode and boss is not 'Arial':
            boss.update()
            boss.reset()
            
            # Проверка столкновений обычных пуль с боссом
            boss_hits = sprite.spritecollide(boss, bullets, True)
            for hit in boss_hits:
                boss.health -= 1
                if boss.health <= 0:
                    bosses_killed += 1
                    boss = 'Arial'
            
            # Проверка столкновений пробивных пуль с боссом
            piercing_boss_hits = sprite.spritecollide(boss, piercing_bullets, False)
            for hit in piercing_boss_hits:
                boss.health -= hit.damage
                if boss.health <= 0:
                    bosses_killed += 1
                    boss = 'Arial'
        
        # Проверка столкновений обычных пуль с обычными врагами
        hits = sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            score += 1
            enemies_killed += 1
            enemy_speed = randint(1, 3)
            # В бесконечном режиме враги становятся быстрее с каждым 5-м убитым врагом
            if endless_mode and score % 5 == 0:
                enemy_speed = min(enemy_speed + 1, 6)  # Максимальная скорость 6
            
            # В бесконечном режиме уменьшаем счетчик пропущенных каждые 10 убитых врагов
            if endless_mode and score % 10 == 0 and missed_enemies > 0:
                missed_enemies -= 1
            
            # Новые враги появляются только если нет босса
            if boss is 'Arial':
                # Создаем столько врагов, сколько было убито, чтобы поддерживать 5 врагов на карте
                for i in range(len(hits)):
                    enemy = Enemy("oreshnik.png", randint(50, 650), -50, enemy_speed, 80, 50)
                    enemies.add(enemy)
        
        # Проверка столкновений пробивных пуль с обычными врагами
        piercing_hits = sprite.groupcollide(enemies, piercing_bullets, True, False)
        for hit in piercing_hits:
            score += 1
            enemies_killed += 1
            # Пробивная пуля НЕ уничтожается при столкновении и продолжает полет
            
            # Новые враги появляются только если нет босса
            if boss is 'Arial':
                enemy = Enemy("oreshnik.png", randint(50, 650), -50, randint(1, 3), 80, 50)
                enemies.add(enemy)
        
        # Проверка столкновения игрока с врагами или боссом
        if sprite.spritecollide(player, enemies, False) or (boss is not 'Arial' and sprite.collide_rect(player, boss)):
            # В бесконечном режиме обновляем рекорд
            if endless_mode and score > high_score:
                high_score = score
            finish = True
            window.blit(lose_text, (200, 150))
        
        # Отображение счета
        score_text = font1.render("Счет: " + str(score), True, (255, 255, 255))
        window.blit(score_text, (10, 10))
        
        # Отображение пропущенных врагов (в обоих режимах)
        missed_text = font1.render("Пропущено: " + str(missed_enemies), True, (255, 255, 255))
        window.blit(missed_text, (10, 50))
        
        if not endless_mode:
            # Обычный режим - показываем цель
            goal_text = font1.render("Цель: " + str(goal), True, (255, 255, 255))
            window.blit(goal_text, (10, 90))
        else:
            # Бесконечный режим - показываем рекорд
            high_score_text = font1.render("Рекорд: " + str(high_score), True, (255, 255, 255))
            window.blit(high_score_text, (10, 90))
            
            # Отображение здоровья босса
            if boss is not 'Arial':
                boss_health_text = font1.render("Босс: " + str(boss.health) + "/" + str(boss.max_health), True, (255, 0, 0))
                window.blit(boss_health_text, (10, 130))
        
        # Отображение состояния музыки
        music_status = "Музыка: ВКЛ" if music_playing else "Музыка: ВЫКЛ"
        music_text = font1.render(music_status, True, (255, 255, 255))
        window.blit(music_text, (10, 170))
        
        # Отображение режима игры
        mode_text = font1.render("Режим: " + ("БЕСКОНЕЧНЫЙ" if endless_mode else "НОРМАЛЬНЫЙ"), True, (255, 255, 255))
        window.blit(mode_text, (10, 210))
        
        # Отображение перезарядки пробивного выстрела
        if piercing_ready:
            piercing_status = "Пробивной: ГОТОВ (Q)"
            piercing_color = (0, 255, 0)
        else:
            piercing_percent = (piercing_max_cooldown - piercing_cooldown) / piercing_max_cooldown
            piercing_status = "Пробивной: " + str(int(piercing_percent * 100)) + "%"
            piercing_color = (255, 255, 0)
        
        piercing_text = font1.render(piercing_status, True, piercing_color)
        window.blit(piercing_text, (10, 250))
        
        # Проверка условий победы/поражения
        if not endless_mode:
            # Обычный режим
            if score >= goal:
                finish = True
                window.blit(win_text, (200, 150))
            
            if missed_enemies >= 3:
                finish = True
                window.blit(lose_text, (200, 150))
        else:
            # Бесконечный режим - поражение при 3 пропущенных врагах
            if missed_enemies >= 3:
                if score > high_score:
                    high_score = score
                finish = True
                window.blit(lose_text, (200, 150))
    
    else:
        # Если игра завершена
        if endless_mode:
            endless_info = font1.render("Бесконечный режим", True, (255, 255, 255))
            window.blit(endless_info, (250, 100))
            final_score = font1.render("Ваш счет: " + str(score), True, (255, 255, 255))
            window.blit(final_score, (280, 240))
            record_text = font1.render("Рекорд: " + str(high_score), True, (255, 255, 0))
            window.blit(record_text, (280, 280))
            # Показываем убитых боссов только если был убит хотя бы один босс
            if bosses_killed > 0:
                bosses_killed_text = font1.render("Убито боссов: " + str(bosses_killed), True, (255, 0, 0))
                window.blit(bosses_killed_text, (260, 320))
        else:
            if score >= goal:
                win_final = font1.render("Победа!", True, (0, 255, 0))
                window.blit(win_final, (300, 240))
            else:
                lose_final = font1.render("Поражение!", True, (255, 0, 0))
                window.blit(lose_final, (280, 240))
        
        restart_text = font1.render("Нажми R для перезапуска", True, (255, 255, 255))
        window.blit(restart_text, (220, 370))
        
        mode_switch_text = font1.render("Нажми G для смены режима", True, (255, 255, 255))
        window.blit(mode_switch_text, (200, 410))
    
    display.update()
    clock.tick(FPS)