import pygame as pg
import os
import random

GAME_PLATFORMS = 8
GAME_PLAYER_WIDTH = 0.05
GAME_PLAYER_HEIGHT = 0.05
GAME_PLATFORM_WIDTH = 0.15
GAME_PLATFORM_HEIGHT = 0.05

main_menu = 0
start_game = 1
game_over = 2

class game:
    def __init__(self):
        pg.init()
        self.WIDTH = 1000
        self.HEIGHT = 1000
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT), pg.RESIZABLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.player = player(0.5 - GAME_PLAYER_WIDTH / 2, 0.1, GAME_PLAYER_WIDTH, GAME_PLAYER_HEIGHT, 0.0, 0.0)
        self.entities = []
        self.wy = 0
        self.dt = 0.0
        self.platform_create(0.5 - GAME_PLATFORM_WIDTH / 2, (GAME_PLATFORMS - 1) / GAME_PLATFORMS, 0.0, 0.0)
        for i in range(0, GAME_PLATFORMS - 1):
            x = random.random() * (1.0 - GAME_PLATFORM_WIDTH)
            y = float(i) / float(GAME_PLATFORMS)
            self.platform_create(x, y, 0, 0)

    def render(self):
        self.screen.fill("white")
        self.player.draw(self.screen, self.wy)
        for entity in self.entities:
            entity.draw(self.screen, self.wy)

    def platform_create(self, x, y, vel_x, vel_y):
        self.entities.append(platform(x, y, GAME_PLATFORM_WIDTH, GAME_PLATFORM_HEIGHT, vel_x, vel_y))

    def collision(self):
        if self.player.getY(self.wy) < 0.25:
            self.wy += 0.25 - self.player.getY(self.wy)
    
        if self.player.getY(self.wy) > 1.0:
            self.player.y = -self.wy

        if self.player.x < -self.player.w:
            self.player.x = 1.0
        if self.player.x > 1.0:
            self.player.x = -self.player.w
        
        for e in self.entities:
            e.collision()
            self.player.collision(e)
            if e.getY(self.wy) > 1.0:
                self.entities.remove(e)
                self.platform_create(random.random() * (1.0 - GAME_PLATFORM_WIDTH), -GAME_PLATFORM_HEIGHT - self.wy, (random.random() * 0.5) if self.moving_platform() else 0.0, 0.0)

    def moving_platform(self):
        return random.random() < 0.2

    def input(self):
        key = pg.key.get_pressed()
        if key[pg.K_RIGHT]:
            self.player.vel_x = 0.3
        elif key[pg.K_LEFT]:
            self.player.vel_x = -0.3
        else:
            self.player.vel_x = 0
    
    def update(self):
        self.player.update(self.dt)
        for e in self.entities:
            e.update(self.dt)

class entity:
    def __init__(self, x, y, w, h, vel_x, vel_y,):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.vel_x = vel_x
        self.vel_y = vel_y

    def draw(self, sf):
        pg.draw.rect(sf,(0,0,0),(self.x,self.y,self.w,self.h))
    
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
        self.texture = pg.image.load(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sprites", "platform.png")).convert_alpha()
        super().__init__(x, y, w, h, vel_x, vel_y)

    def draw(self, sf, wy):
        (WIDTH, HEIGHT) = sf.get_size()
        img = pg.transform.scale(self.texture, (self.w * WIDTH,self.h * HEIGHT))
        sf.blit(img, (self.x * WIDTH,self.getY(wy) * HEIGHT))

    def collision(self):
        if self.x < 0.0:
            self.vel_x = -self.vel_x 
            self.x = 0.0
        
        if self.x > 1.0 - self.w:
            self.vel_x = -self.vel_x
            self.x = 1.0 - self.w
        
class player(entity):
    def __init__(self, x, y, w, h, vel_x, vel_y):
        self.texture = pg.image.load(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sprites", "player.png")).convert_alpha()
        super().__init__(x, y, w, h, vel_x, vel_y)

    def update(self, dt):
        self.vel_x += 0.0 * dt
        self.vel_y += 0.5 * dt
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

    def collision(self, pf):
        if self.overlap(pf) and self.vel_y > 0.00:
            self.vel_y = -0.75 
            self.y = pf.y - self.h

    def draw(self, sf, wy):
        (WIDTH, HEIGHT) = sf.get_size()
        img = pg.transform.scale(self.texture, (self.w * WIDTH,self.h * HEIGHT))
        sf.blit(img, (self.x * WIDTH,self.getY(wy) * HEIGHT))

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
        
        pg.display.flip()
        g.dt = g.clock.tick(60) / 1000.0
    
    pg.quit()

if __name__ == '__main__':
    main()