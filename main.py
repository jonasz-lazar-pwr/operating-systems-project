import random
import sys
import time

import pygame
import threading


class Game:
    def __init__(self):
        self.elapsed_time = 0.0
        self.player_pos = [128, 0]
        self.cars = []
        self.collided_cars = set()
        pygame.init()
        pygame.display.set_caption("operating-systems-project")
        self.player_img = pygame.image.load("assets/player_sprite.png")
        self.car_1_img = pygame.image.load("assets/car_1.png")
        self.car_images = [
            pygame.image.load("assets/car_1.png"),
            pygame.image.load("assets/car_2.png"),
            pygame.image.load("assets/car_3.png")
        ]
        self.background_img = pygame.image.load("assets/background.png")
        self.screen = pygame.display.set_mode((400, 600))
        self.lives = 3
        self.has_finished = False

        # initialize font
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 30)

        # initialize timer
        self.start_time = time.time()

        # threading events (mutexes?) for synchronization
        self.draw_flag = threading.Event()
        self.draw_flag.set()

        # lock access to screen
        self.screen_lock = threading.Lock()
        # lock access to cars
        self.cars_lock = threading.Lock()

        # create and start the thread handling drawing
        self.drawing_thread = threading.Thread(target=self.draw_loop)
        self.drawing_thread.start()

        # add cars at the very beggining of the game
        self.add_initial_cars()

        # create and start the thread generating and moving cars
        self.generate_traffic_thread = threading.Thread(target=self.generate_traffic_loop)
        self.generate_traffic_thread.start()
        self.traffic_thread = threading.Thread(target=self.traffic_loop)
        self.traffic_thread.start()

        # main game loop
        self.main_loop()

    def add_initial_cars(self):
        initial_car_positions = [
            [128, 64, random.randint(0, len(self.car_images) - 1)],
            [384, 64, random.randint(0, len(self.car_images) - 1)],
            [352, 192, random.randint(0, len(self.car_images) - 1)],
            [480, 192, random.randint(0, len(self.car_images) - 1)],
            [288, 320, random.randint(0, len(self.car_images) - 1)],
            [448, 320, random.randint(0, len(self.car_images) - 1)],
            [128, 448, random.randint(0, len(self.car_images) - 1)],
            [384, 448, random.randint(0, len(self.car_images) - 1)]
        ]
        with self.cars_lock:
            self.cars.extend(initial_car_positions)

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
                self.screen.blit(self.car_images[car[2]], (car[0], car[1]))

            # draw lives text
            lives_text = self.font.render(f"Lives: {self.lives}", True, (255, 255, 255))
            self.screen.blit(lives_text, (10, 10))

            # draw timer
            if not self.has_finished:
                self.elapsed_time = time.time() - self.start_time

            timer_text = self.font.render(f"{round(self.elapsed_time, 2)}", True, (255, 255, 255))
            self.screen.blit(timer_text, (300, 10))

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
                    elif event.key == pygame.K_r:
                        self.reset_game()

            # check for collisions
            self.check_collisions()

            # check if player won
            if self.player_pos[1] >= 512:
                self.has_finished = True
                self.game_won()
            # check if game over
            if self.lives <= 0:
                self.game_over()

            # allow drawing
            self.draw_flag.set()

    # game over screen
    def game_over(self):
        with self.screen_lock:
            self.has_finished = True
            self.draw_flag.clear()
            self.screen.fill((0, 0, 0))
            game_over_text = self.font.render("Game Over!", True, (255, 255, 255))
            self.screen.blit(game_over_text, (100, 250))
            pygame.display.flip()
        # wait for a moment before exiting
        pygame.time.delay(3000)
        pygame.quit()
        sys.exit(0)

    # game won screen
    def game_won(self):
        with self.screen_lock:
            self.has_finished = True
            self.draw_flag.clear()
            self.screen.fill((0, 0, 0))
            game_won_text = self.font.render('You won!', True, (255, 255, 255))
            elapsed_time_text = self.font.render(f'{round(self.elapsed_time, 2)}', True, (255, 0, 255))
            best_time_file = open('scores', 'r')
            current_best_time = float(best_time_file.read())
            current_best_time_text = self.font.render(f'Best time: {current_best_time}', True, (0, 255, 255))

            if self.elapsed_time < current_best_time:
                best_time_file = open('scores', 'w')
                best_time_file.write(f'{round(self.elapsed_time, 2)}')

            self.screen.blit(game_won_text, (140, 250))
            self.screen.blit(elapsed_time_text, (160, 350))
            self.screen.blit(current_best_time_text, (100, 450))
            pygame.display.flip()

    # check for collisions between player and cars
    def check_collisions(self):
        margin_x = 10
        margin_y = 10
        player_rect = pygame.Rect(
            self.player_pos[0] + margin_x,
            self.player_pos[1] + margin_y,
            self.player_img.get_width() - 2 * margin_x,
            self.player_img.get_height() - 2 * margin_y
        )
        with self.cars_lock:
            for index, car in enumerate(self.cars):
                car_rect = pygame.Rect(
                    car[0] + margin_x,
                    car[1] + margin_y,
                    self.car_1_img.get_width() - 2 * margin_x,
                    self.car_1_img.get_height() - 2 * margin_y
                )
                if player_rect.colliderect(car_rect) and index not in self.collided_cars:
                    self.lives -= 1
                    self.player_pos = [128, 0]
                    self.collided_cars.add(index)
                    print(f"Lives left: {self.lives}")
            # remove cars that are no longer colliding
            self.collided_cars = {index for index in self.collided_cars if index < len(self.cars) and player_rect.colliderect(pygame.Rect(self.cars[index][0], self.cars[index][1], self.car_1_img.get_width(), self.car_1_img.get_height()))}

    # thread drawing objects on screen
    def draw_loop(self):
        while True:
            # wait till there is permission
            self.draw_flag.wait()
            # do the drawing
            if not self.has_finished:
                self.draw_objects()
            # prevent further drawing with no permission
            self.draw_flag.clear()

    # thread generating cars
    def generate_traffic_loop(self):
        lane_delays = [random.randint(2000, 5000) for _ in range(4)]
        last_spawn_times = [pygame.time.get_ticks() for _ in range(4)]
        lanes = [64, 192, 320, 448]

        while True:
            current_time = pygame.time.get_ticks()
            for i, lane in enumerate(lanes):
                if current_time - last_spawn_times[i] >= lane_delays[i]:
                    car_type = random.randint(0, len(self.car_images) - 1)
                    with self.cars_lock:
                        self.cars.append([464, lane, car_type])
                    lane_delays[i] = random.randint(2000, 5000)
                    last_spawn_times[i] = current_time
            pygame.time.delay(100)

    # thread moving cars
    def traffic_loop(self):
        while True:
            with self.cars_lock:
                for car in self.cars:
                    car[0] -= 1
                # remove cars when they are out of bounds
                self.cars = [car for car in self.cars if car[0] >= -64]
            pygame.time.delay(10)

    # allow reseting game
    def reset_game(self):
        self.elapsed_time = 0.0
        self.player_pos = [128, 0]
        self.cars = []
        self.collided_cars = set()
        self.lives = 3
        self.has_finished = False
        self.start_time = time.time()
        self.add_initial_cars()


game = Game()
