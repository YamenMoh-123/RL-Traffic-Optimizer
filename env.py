import pygame
import sys

pygame.init()

# Grid size definition - easily modifiable
GRID_SIZE = 10
width, height = 800, 600
GRID_COLS, GRID_ROWS = width // GRID_SIZE, height // GRID_SIZE

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Pygame Frame')

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Car:
    def __init__(self, color, grid_position):
        self.color = color
        self.grid_position = list(grid_position)  # Make a copy of the position

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, pygame.Rect(
            self.grid_position[0] * GRID_SIZE,
            self.grid_position[1] * GRID_SIZE,
            GRID_SIZE, GRID_SIZE))


class TrafficLight:
    def __init__(self, grid_position, initially_green=True):
        self.grid_position = grid_position
        self.is_green = initially_green

    def toggle(self):
        self.is_green = not self.is_green

    def draw(self, screen):
        color = (0, 255, 0) if self.is_green else (255, 0, 0)
        pygame.draw.circle(screen, color, (self.grid_position[0] * GRID_SIZE + GRID_SIZE // 2, self.grid_position[1] * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 2)


class Lane:
    def __init__(self, start_grid_pos, end_grid_pos, color=(255, 255, 255)):
        self.start_grid_pos = start_grid_pos
        self.end_grid_pos = end_grid_pos
        self.cars = []
        self.color = color
        self.direction = 'horizontal' if start_grid_pos[1] == end_grid_pos[1] else 'vertical'

    def add_car(self, color):
        # New cars are added to the start of the lane
        self.cars.append(Car(color, self.start_grid_pos))

    def update_cars(self):

        for car in self.cars:
            if self.direction == 'horizontal':
                car.grid_position[0] += 1  # Move right
            elif self.direction == 'vertical':
                car.grid_position[1] += 1  # Move down

    def draw(self, screen):
        pygame.draw.line(screen, self.color,
            (self.start_grid_pos[0] * GRID_SIZE, self.start_grid_pos[1] * GRID_SIZE),
            (self.end_grid_pos[0] * GRID_SIZE, self.end_grid_pos[1] * GRID_SIZE),
            GRID_SIZE // 2)  # Use half of GRID_SIZE for line width
        for car in self.cars:
            car.draw(screen)

lanes = [
    Lane((35, 0), (35, 60)),
    Lane((45, 0), (45, 60)),
    Lane((0, 25), (80, 25)),
    Lane((0, 35), (80, 35)),
]

# Add a car to a specific lane
lanes[0].add_car((255, 0, 0))

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    for lane in lanes:
        lane.update_cars()
        lane.draw(screen)

    pygame.display.flip()
    clock.tick(20)

pygame.quit()
sys.exit()
