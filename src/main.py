import pygame as pg
import os
import random

GAME_PLAYER_WIDTH = 0.05
GAME_PLAYER_HEIGHT = 0.05

GAME_PLATFORMS = 8
GAME_PLATFORM_WIDTH = 0.15
GAME_PLATFORM_HEIGHT = 0.05

GAME_BOOST_WIDTH = 0.05
GAME_BOOST_HEIGHT = 0.05

GAME_MENU = 0
GAME_RUNNING = 1
GAME_OVER = 2

TEXTURE_NONE = 0
TEXTURE_MELON = 1
TEXTURE_ORANGE = 2
TEXTURE_BOOST = 3
TEXTURE_PLATFORM = 4
TEXTURE_PLAYER = 5
TEXTURE_BACKGROUND = 6
TEXTURE_LOGO = 7

class game:
    def __init__(self):
        pg.init()
        self.WIDTH = 1000
        self.HEIGHT = 1000
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT), pg.RESIZABLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font = pg.font.Font("font.ttf", 64)
        self.game_status = GAME_MENU
        self.wy = 0
        self.dt = 1.0
        self.player = player(0.5 - GAME_PLAYER_WIDTH / 2, 0.1, GAME_PLAYER_WIDTH, GAME_PLAYER_HEIGHT, 0.0, 0.0)
        self.entities = []
        self.score_points = 0.0
        self.highscore = 0.0
        self.textures =  [
            pg.image.load(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sprites", "none.png")).convert_alpha(),
            pg.image.load(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sprites", "melon.png")).convert_alpha(), 
            pg.image.load(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sprites", "orange.png")).convert_alpha(),
            pg.image.load(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sprites", "boost.png")).convert_alpha(),
            pg.image.load(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sprites", "platform.png")).convert_alpha(),
            pg.image.load(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sprites", "player.png")).convert_alpha(),
            pg.image.load(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sprites", "background.png")).convert_alpha(),
            pg.image.load(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sprites", "logo.png")).convert_alpha()
            ]

        self.highscore_load()
        self.start()

    def __del__(self):
        self.highscore_save()

    def render(self):
        self.render_background()
        
        if self.game_status != GAME_OVER and self.game_status != GAME_MENU:
            self.player.draw(self.screen, self.wy, self.textures)
            self.render_score()
            self.render_entities()       
        elif self.game_status != GAME_RUNNING and self.game_status != GAME_MENU:
            self.render_death_screen()
        elif  self.game_status != GAME_RUNNING and self.game_status != GAME_OVER:
            self.render_menu()

    def render_logo(self):
        logo = pg.transform.scale(self.textures[TEXTURE_LOGO], (self.WIDTH // 0.95 , self.HEIGHT // 2))
        self.screen.blit(logo, (0, 0))

    def render_start_option(self):
        start_option = self.font.render("PRESS SPACE TO START!", True, "black")
        self.screen.blit(start_option, (self.WIDTH // 6, self.HEIGHT // 1.5))

    def render_menu(self):
        self.render_logo()
        self.render_start_option()

    def render_entities(self):
        if self.game_status != GAME_MENU and self.game_status != GAME_OVER:
            for entity in self.entities:
                entity.draw(self.screen, self.wy, self.textures)

    def highscore_load(self):
        try:
            with open ("high_score.txt", mode="r") as file:
                self.highscore = float(file.read())
        except FileNotFoundError:
            self.highscore = 0.0

    def highscore_save(self):
        try:
            with open("high_score.txt", mode="w") as file:
                file.write(str(self.highscore))
        except FileNotFoundError:
            self.highscore = 0.0

    def render_death_screen(self):
        death_msg = self.font.render("YOU DIED!", True, "black") 
        restart_option = self.font.render("PRESS SPACE TO RESTART!", True, "black")
        death_score_msg = self.font.render("YOU REACHED:", True, "black")
        death_score = self.font.render(f"A SCORE OF  {int(self.score_points)}", True, "black")
        self.screen.blit(death_score, (self.WIDTH // 3.25, self.HEIGHT // 2.25))
        self.screen.blit(death_score_msg, (self.WIDTH // 3.25, self.HEIGHT // 2.75))
        self.screen.blit(death_msg, (self.WIDTH // 2.75, self.HEIGHT // 5))
        self.screen.blit(restart_option, (self.WIDTH // 7, self.HEIGHT // 1.5))

    def platform_create(self, x, y, vel_x, vel_y):
        self.entities.append(platform(x, y, GAME_PLATFORM_WIDTH, GAME_PLATFORM_HEIGHT, vel_x, vel_y))

    def boost_create(self, x, y, vel_x, vel_y):
        self.entities.append(boost(x, y, GAME_BOOST_WIDTH, GAME_BOOST_HEIGHT, vel_x, vel_y)) 

    def collision(self):
        if self.game_status != GAME_OVER and self.game_status != GAME_MENU:
            if self.player.getY(self.wy) < 0.25:
                self.wy += 0.25 - self.player.getY(self.wy)

            if self.player.x < -self.player.w:
                self.player.x = 1.0
            if self.player.x > 1.0:
                self.player.x = -self.player.w

            for e in self.entities:
                e.collision()
                self.player.collision(e)
                if e.getY(self.wy) > 1.0:
                    self.entities.remove(e)
                    if isinstance(e, platform):
                        self.platform_create(random.random() * (1.0 - GAME_PLATFORM_WIDTH), -GAME_PLATFORM_HEIGHT - self.wy, (random.random() * 0.5) if self.moving_platform() else 0.0, 0.0)
                    elif isinstance(e, boost):
                        self.boost_create(random.random() * (1.0 - GAME_BOOST_WIDTH), -GAME_BOOST_HEIGHT - self.wy, 0.0, 0.0)

    def moving_platform(self):
        return random.random() < 0.2

    def start(self):
        self.game_status = GAME_MENU

    def reset(self):
        self.game_status = GAME_RUNNING
        self.wy = 0
        self.dt = 0.0
        self.score_points = 0.0
        
        self.player = player(0.5 - GAME_PLAYER_WIDTH / 2, 0.1, GAME_PLAYER_WIDTH, GAME_PLAYER_HEIGHT, 0.0, 0.0)
        self.entities = []
        self.platform_create(0.5 - GAME_PLATFORM_WIDTH / 2, (GAME_PLATFORMS - 1) / GAME_PLATFORMS, 0.0, 0.0)
        self.boost_create(random.random() * (1.0 - GAME_BOOST_WIDTH), -GAME_BOOST_HEIGHT - self.wy, 0.0, 0.0)
        
        for i in range(0, GAME_PLATFORMS - 1):
            x = random.random() * (1.0 - GAME_PLATFORM_WIDTH)
            y = float(i) / float(GAME_PLATFORMS)
            self.platform_create(x, y, 0, 0)

    def render_background(self):
        background = pg.transform.scale(self.textures[TEXTURE_BACKGROUND], (self.WIDTH, self.HEIGHT))
        self.screen.blit(background, (0, 0))

    def render_score(self):
        self.score()
        score_text = self.font.render(f"Score: {int(self.score_points)}", True, "black") 
        self.screen.blit(score_text, (self.WIDTH // 1.5, self.HEIGHT // 10))

        high_score_death = self.font.render(f"High Score: {int(self.highscore)}", True, "black")
        self.screen.blit(high_score_death, (self.WIDTH // 1.82, self.HEIGHT // 6))

    def score(self):
        if self.player.getY(self.wy) < 0.3 and self.player.vel_y < 0:
            self.score_points += 0.1

        if self.highscore < self.score_points:
            self.highscore = self.score_points 

    def input(self):
        key = pg.key.get_pressed()
        if self.game_status != GAME_OVER:
            if key[pg.K_RIGHT]:
                self.player.vel_x = 0.3
            elif key[pg.K_LEFT]:
                self.player.vel_x = -0.3
            else:
                self.player.vel_x = 0
            if self.game_status != GAME_MENU:    
                if self.player.getY(self.wy) > 1.0:
                    self.game_status = GAME_OVER
                    self.highscore_save()
        else:
            if key[pg.K_SPACE]:
                self.reset()
        if self.game_status == GAME_MENU:
              if key[pg.K_SPACE]:
                self.reset()
    
    def update(self):
        if self.game_status != GAME_OVER:
            self.player.update(self.dt)
            for e in self.entities:
                e.update(self.dt)

class entity:
    def __init__(self, x, y, w, h, vel_x, vel_y):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.texture = TEXTURE_NONE

    def draw(self, sf, wy, textures):
        pg.draw.rect(sf,(0,0,0),(self.x,self.y ,self.w,self.h))

    def overlap(self, ent):
        if not ( self.y < ent.y - self.h  or self.y > ent.y + ent.h or self.x < ent.x - self.w or self.x > ent.x + ent.w):
            return True
        else:
            return False

    def getY(self, wy):
        return self.y + wy

    def update(self, dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

class platform(entity):
    def __init__(self, x, y, w, h, vel_x, vel_y):
        super().__init__(x, y, w, h, vel_x, vel_y)
        self.texture = TEXTURE_PLATFORM
        
    def collision(self):
        if self.x < 0.0:
            self.vel_x = -self.vel_x 
            self.x = 0.0
        
        if self.x > 1.0 - self.w:
            self.vel_x = -self.vel_x
            self.x = 1.0 - self.w

    def draw(self, sf, wy, textures):
        (WIDTH, HEIGHT) = sf.get_size()
        img = pg.transform.scale(textures[self.texture], (self.w * WIDTH,self.h * HEIGHT))
        sf.blit(img, (self.x * WIDTH,self.getY(wy) * HEIGHT))

class player(entity):
    def __init__(self, x, y, w, h, vel_x, vel_y):
        super().__init__(x, y, w, h, vel_x, vel_y)
        self.texture = TEXTURE_PLAYER

    def update(self, dt):
        self.vel_x += 0.0 * dt
        self.vel_y += 0.5 * dt
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

    def collision(self, object):   
            if isinstance(object, boost):
                if self.overlap(object):
                    self.vel_y = -1.5        
            elif isinstance(object, platform):
                if self.overlap(object) and self.vel_y > 0.00:
                    self.vel_y = -0.75 
                    self.y = object.y - self.h

    def draw(self, sf, wy, textures):
        (WIDTH, HEIGHT) = sf.get_size()
        img = pg.transform.scale(textures[self.texture], (self.w * WIDTH, self.h * HEIGHT))
        sf.blit(img, (self.x * WIDTH, self.getY(wy) * HEIGHT))

class boost(entity):
    def __init__(self, x, y, w, h, vel_x, vel_y):
        super().__init__(x, y, w, h, vel_x, vel_y)
        if random.random() >= 0.8:
            self.texture = TEXTURE_MELON
        elif random.random() >= 0.6 :
            self.texture = TEXTURE_ORANGE
        else:
            self.texture = TEXTURE_BOOST

    def collision(self):
        pass

    def draw(self, sf, wy, textures):
        (WIDTH, HEIGHT) = sf.get_size()
        img = pg.transform.scale(textures[self.texture], (self.w * WIDTH, self.h * HEIGHT))
        sf.blit(img, (self.x * WIDTH, self.getY(wy) * HEIGHT))

def main():
    g = game()
    
    while g.running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                g.running = False
            if event.type == pg.WINDOWSIZECHANGED:
                g.WIDTH, g.HEIGHT = pg.display.get_surface().get_size()

        g.input()
        g.update()
        g.collision()
        g.render()

        if g.dt != 0.0 :
            pg.display.set_caption(f"Monkey Jumper | fps:{int(1/g.dt)}")

        pg.display.flip()
        g.dt = g.clock.tick(200) / 1000.0
    
    pg.quit()

if __name__ == '__main__':
    main()