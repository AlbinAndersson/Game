import pygame
import math
import logging
import sys
from random import randint

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

SCREEN_SIZE = (800, 600)

class Controller():

    PRESTART = 1
    RUNNING = 2
    GAMEOVER = 3

    def __init__(self):
        self.events = {}
        self.keymap = {}

        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption('Epic Game')
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font("font/Roboto-Black.ttf", 50)
        self.cubewin_surface = pygame.Surface((SCREEN_SIZE[0] - 120, SCREEN_SIZE[1] - 120))
        text = self.font.render('YOU WIN!', 1, pygame.Color('#FFFFFF'))
        self.cubewin_surface.blit(text, ((self.cubewin_surface.get_width() - text.get_width()) / 2,
                                          (self.cubewin_surface.get_height() - text.get_height()) / 2))

        self.register_eventhandler(pygame.QUIT, self.quit)
        self.register_key(pygame.K_ESCAPE, self.quit)
        self.register_key(pygame.K_r, self.restart)

        self.world = World(self)
        self.cube = Cube(self)
        self.life = Life(self)
        self.enemy = [Enemy(self), Enemy(self), Enemy(self), Enemy(self)]
        self.second = 0
        self.count = 0
        self.fps = 60
        self.S = randint(-50, 50) / 100


        self.game_state = Controller.PRESTART


    def run(self):
        self.game_state = Controller.RUNNING

        while True:
            # -- Handle all events -------------------------------------------
            for event in pygame.event.get():
                logger.debug('Handling event {}'.format(event))

                # Handle events
                for event_type, callbacks in self.events.items():
                    if event.type == event_type:
                        for callback in callbacks:
                            callback(event)

                # Handle keypresses
                if event.type == pygame.KEYDOWN:
                    for key in self.keymap.keys():
                        if event.key == key:
                            for callback in self.keymap[key]:
                                callback(event)

            # -- alla uppdateringar som händer under spelets gång----------------
            self.life.update()
            for enemy in self.enemy:
                enemy.update()
            self.cube.update()
            if (self.cube.x - self.cube.size / 2 - self.life.size / 2) <= self.life.x <= self.cube.x + self.cube.size / 2 + self.life.size / 2:
                if (self.cube.y - self.cube.size / 2 - self.life.size / 2) <= self.life.y <= self.cube.y + self.cube.size / 2 + self.life.size / 2:
                    self.life.reset()
                    if self.cube.size < 300:
                        self.cube.size = self.cube.size * 1.1
                        self.cube.point -= (self.cube.size * 1.1) - self.cube.size
            if self.cube.point <= 0:
                self.game_state = Controller.GAMEOVER

            for enemy in self.enemy:
                if (self.cube.x - self.cube.size / 2 - enemy.size / 2) <= enemy.x <= self.cube.x + self.cube.size / 2 + enemy.size / 2:
                    if (self.cube.y - self.cube.size / 2 - enemy.size / 2) <= enemy.y <= self.cube.y + self.cube.size / 2 + enemy.size / 2:
                        enemy.reset()
                        if self.cube.size >= 10:
                            self.cube.size = self.cube.size * 0.8
                            self.cube.point -= (self.cube.size * 0.8) - self.cube.size

            self.count += 1
            if self.count % self.fps == 0:
                self.second += 1

            white = pygame.Color('#FFFFFF')
            message = 'Tid {} Sekunder'.format(self.second)
            font_time = pygame.font.Font("font/Roboto-Black.ttf", 25)
            text = font_time.render(message, 1, white)


            # -- Ritar upp allt på skärmen -----------------------------------
            if self.game_state == Controller.RUNNING:
                self.world.draw()
                self.cube.draw()
                self.life.draw()
                for enemy in self.enemy:
                    enemy.draw()
                self.screen.blit(text, (10, 1))

            if self.game_state == Controller.GAMEOVER:
                self.cube.y_speed = 0
                self.cube.x_speed = 0
                self.screen.blit(self.cubewin_surface, (60, 60))




            pygame.display.flip()

            self.clock.tick(60)


    def quit(self, event):
        logger.info('Quitting... Good bye!')
        pygame.quit()
        sys.exit()

    def restart(self, event):
        logger.info('Restarting....')
        self.cube.reset()
        self.game_state = Controller.RUNNING
        self.life.reset()
        for enemy in self.enemy:
            enemy.reset()


    def register_eventhandler(self, event_type, callback):
        logger.debug('Registering event handler ({}, {})'.format(event_type, callback))
        if self.events.get(event_type):
            self.events[event_type].append(callback)
        else:
            self.events[event_type] = [callback]


    def register_key(self, key, callback):
        logger.debug('Binding key {} to {}.'.format(key, callback))
        if self.keymap.get(key):
            self.keymap[key].append(callback)
        else:
            self.keymap[key] = [callback]

#------------ spelaren du styr ------------------------------------------------

class Cube():
    def __init__(self, controller):
        self.controller = controller
        self.screen = controller.screen

        self.controller.register_eventhandler(pygame.KEYDOWN, self.keydown)
        self.controller.register_eventhandler(pygame.KEYUP, self.keyup)

        self.colors = {'cube': pygame.Color('#A7E855'),
                       'life': pygame.Color('#6FE8E0'),
                       'point':  pygame.Color('#FF4ADC')}

        self.reset()

    def reset(self):
        self.x = SCREEN_SIZE[0] / 2
        self.y = 100
        self.y_speed = 0
        self.x_speed = 0
        self.main_booster = False
        self.left_booster = False
        self.right_booster = False
        self.down_booster = False
        self.size = 10
        self.point = 300

    def draw(self):
        surface = pygame.Surface((self.size, self.size), flags=pygame.SRCALPHA)
        surface.fill(self.colors['cube'], (0, 0, self.size, self.size))
        self.screen.blit(surface, (self.x - self.size / 2, self.y - self.size / 2))

        point = pygame.Surface(( 8, SCREEN_SIZE[1]))
        point.fill(self.colors['point'], (0, 0, 8, self.point / 300 * SCREEN_SIZE[1]))
        self.screen.blit(point, (0, 0))

    def update(self):

        if self.x < 15 + self.size / 2:
            self.x = 15 + self.size / 2
            self.x_speed = 0

        elif self.x > SCREEN_SIZE[0] - 10 - self.size / 2:
            self.x = SCREEN_SIZE[0] - 10 - self.size / 2
            self.x_speed = 0

        if self.y < 10 + self.size / 2:
            self.y = 10 + self.size / 2
            self.y_speed = 0

        elif self.y > SCREEN_SIZE[1] - 10 - self.size / 2:
            self.y = SCREEN_SIZE[1] - 10 - self.size / 2
            self.y_speed = 0

        if self.main_booster:
            self.y_speed -= .1

        else:
            self.y_speed += 0

        if self.down_booster:
            self.y_speed += .1


        if self.left_booster:
            self.x_speed += 0.1


        if self.right_booster:
            self.x_speed -= 0.1


        if not self.right_booster and not self.left_booster:
            self.x_speed = self.x_speed * 0.90

        if not self.down_booster and not self.main_booster:
            self.y_speed = self.y_speed * 0.90

        # Calculate new position
        self.x = self.x + self.x_speed
        self.y = self.y + self.y_speed


    def keydown(self, event):
        if event.key == pygame.K_UP:
            self.main_booster = True

        if event.key == pygame.K_DOWN:
            self.down_booster = True

        if event.key == pygame.K_LEFT:
            self.right_booster = True

        if event.key == pygame.K_RIGHT:
            self.left_booster = True


    def keyup(self, event):
        if event.key == pygame.K_UP:
            self.main_booster = False

        if event.key == pygame.K_DOWN:
            self.down_booster = False

        if event.key == pygame.K_LEFT:
            self.right_booster = False

        if event.key == pygame.K_RIGHT:
            self.left_booster = False

#------------- kuben du ska fånga --------------------------------------

class Life():
    def __init__(self, controller):
        self.controller = controller
        self.screen = controller.screen

        self.colors = pygame.Color('#FFC951')
        self.size = 10
        self.reset()

    def update(self):

        if self.x < 15:
            self.y = randint(20, 570)
            self.x = randint(20, 570)
            self.x_speed = randint(-200, 200) / 100
            self.y_speed = randint(-200, 200) / 100

        elif self.x > SCREEN_SIZE[0] - 10:
            self.y = randint(20, 570)
            self.x = randint(20, 570)
            self.x_speed = randint(-200, 200) / 100
            self.y_speed = randint(-200, 200) / 100

        if self.y < 10:
            self.y = randint(20, 570)
            self.x = randint(20, 570)
            self.x_speed = randint(-200, 200) / 100
            self.y_speed = randint(-200, 200) / 100

        elif self.y > SCREEN_SIZE[1] - 10:
            self.y = randint(20, 570)
            self.x = randint(20, 570)
            self.x_speed = randint(-200, 200) / 100
            self.y_speed = randint(-200, 200) / 100


        self.y = self.y + self.y_speed
        self.x = self.x + self.x_speed

    def draw(self):
        surface = pygame.Surface((self.size, self.size), flags = pygame.SRCALPHA)
        surface.fill(self.colors, (0, 0, self.size, self.size))
        self.screen.blit(surface, (self.x - self.size / 2, self.y - self.size / 2))



    def reset(self):
        self.x = randint(20, 780)
        self.y = randint(20, 580)
        self.x_speed = randint(5, 50) / 10
        self.y_speed = randint(5, 50) / 10
        logger.debug('Generating new location for life. ({}, {})'.format(self.x, self.y))

        cube = self.controller.cube
        if cube.x - cube.size / 2 < self.x < cube.x + cube.size / 2:
            if cube.x + cube.size / 2 < self.y < cube.y + cube.size / 2:
                self.x = randint(20, 780)
                self.y = randint(20, 580)

#------------------ kuben du ska akta dig för ---------------------------

class Enemy():
    def __init__(self, controller):
        self.controller = controller
        self.screen = controller.screen

        self.colors = pygame.Color('#F73351')
        self.size = 20
        self.reset()
        self.x_speed = randint(-50, 50) / 100
        self.y_speed = randint(-50, 50) / 100


    def update(self):

        if self.x < 15:
            self.y = randint(30, 570)
            self.x = randint(30, 570)
            self.x_speed = self.S
            self.y_speed = self.S

        elif self.x > SCREEN_SIZE[0] - 10:
            self.y = randint(30, 570)
            self.x = randint(30, 570)
            self.x_speed = self.S
            self.y_speed = self.S

        if self.y < 10:
            self.y = randint(30, 570)
            self.x = randint(30, 570)
            self.x_speed = self.S
            self.y_speed = self.S

        elif self.y > SCREEN_SIZE[1] - 10:
            self.y = randint(30, 570)
            self.x = randint(30, 570)
            self.x_speed = self.S
            self.y_speed = self.S


        self.y = self.y + self.y_speed
        self.x = self.x + self.x_speed

    def draw(self):
        surface = pygame.Surface((self.size, self.size), flags = pygame.SRCALPHA)
        surface.fill(self.colors, (0, 0, self.size, self.size))
        self.screen.blit(surface, (self.x - self.size / 2, self.y - self.size / 2))

    def reset(self):
        self.x = randint(30, 770)
        self.y = randint(30, 570)
        self.x_speed = self.S
        self.y_speed = self.S
        logger.debug('Generating new location for enemy. ({}, {})'.format(self.x, self.y))

        cube = self.controller.cube
        if cube.x - cube.size / 2 < self.x < cube.x + cube.size / 2:
            if cube.x + cube.size / 2 < self.y < cube.y + cube.size / 2:
                self.x = randint(30, 770)
                self.y = randint(30, 570)

class World():
    def __init__(self, controller):
        self.controller = controller
        self.screen = controller.screen


    def draw(self):
        surface = pygame.Surface(SCREEN_SIZE)
        surface.fill(pygame.Color('#111111'), (0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1]))
        self.screen.blit(surface, (0, 0))


if __name__ == "__main__":
    c = Controller()
    c.run()
