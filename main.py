import sys
import time

import pygame
import threading


class Game:
    def __init__(self):
        self.player_pos = [64, 64]
        self.cars = []
        pygame.init()
        pygame.display.set_caption("operating-systems-project")
        self.player_img = pygame.image.load("assets/player_sprite.png")
        self.car_1_img = pygame.image.load("assets/car_1.png")
        self.background_img = pygame.image.load("assets/background.png")
        self.screen = pygame.display.set_mode((400, 600))

        # threading events (mutexes?) for synchronization
        self.draw_flag = threading.Event()
        self.draw_flag.set()

        # lock access to screen
        self.screen_lock = threading.Lock()

        # create and start the thread handling drawing
        self.drawing_thread = threading.Thread(target=self.draw_loop)
        self.drawing_thread.start()

        # create and start the thread generating and moving cars
        self.generate_traffic_thread = threading.Thread(target=self.generate_traffic_loop)
        self.generate_traffic_thread.start()
        self.traffic_thread = threading.Thread(target=self.traffic_loop)
        self.traffic_thread.start()

        # main game loop
        self.main_loop()

    # function drawing game objects
    def draw_objects(self):
        with self.screen_lock:
            self.screen.fill((0, 0, 0))
            # draw background
            self.screen.blit(self.background_img, (0, 0))
            # draw player
            self.screen.blit(self.player_img, (self.player_pos[0], self.player_pos[1]))
            # draw all cars
            for car in self.cars:
                self.screen.blit(self.car_1_img, (car[0], car[1]))
            pygame.display.flip()

    # handling keyboard input
    def main_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.player_pos[1] -= 64
                    elif event.key == pygame.K_a:
                        self.player_pos[0] -= 64
                    elif event.key == pygame.K_s:
                        self.player_pos[1] += 64
                    elif event.key == pygame.K_d:
                        self.player_pos[0] += 64

            # allow drawing
            self.draw_flag.set()

    # thread drawing objects on screen
    def draw_loop(self):
        while True:
            # wait till there is permission
            self.draw_flag.wait()
            # do the drawing
            self.draw_objects()
            # prevent further drawing with no permission
            self.draw_flag.clear()

    # thread generating cars
    def generate_traffic_loop(self):
        while True:
            car_1 = [464, 64]
            car_2 = [464, 192]
            car_3 = [464, 320]
            car_4 = [464, 448]
            self.cars.append(car_1)
            self.cars.append(car_2)
            self.cars.append(car_3)
            self.cars.append(car_4)
            pygame.time.delay(4000)

    # thread moving cars
    def traffic_loop(self):
        while True:
            # TODO remove cars when they are out of bounds!!!
            for car in self.cars:
                car[0] -= 1
                print(self.cars)

            pygame.time.delay(10)


game = Game()
