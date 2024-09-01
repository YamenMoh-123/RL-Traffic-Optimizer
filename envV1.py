import pygame
import sys

pygame.init()
width, height = 800, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)

GRID_SIZE = 10
INTERSECTION = 50

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Pygame Frame')


class TrafficLight:
    def __init__(self, x, y):
        self.x = x
        self.y = y


        # to the right drawing, make object with status?, offset off middle?
        #  boundary = [[x,y,width,height], [startX, startY, endX, endY]]
        # convert to objects

        self.N_boundary = [[x, (y-INTERSECTION-int(INTERSECTION/2)), INTERSECTION, int(INTERSECTION/2)], [x, y+INTERSECTION, x+INTERSECTION, y+INTERSECTION], "RED"]  # right
        self.E_boundary = [[x+INTERSECTION, y, int(INTERSECTION/2), INTERSECTION], [x-INTERSECTION, y, x-INTERSECTION, y+INTERSECTION], "RED"]  # down
        self.S_boundary = [[x-INTERSECTION, y+INTERSECTION, INTERSECTION, int(INTERSECTION/2)], [x-INTERSECTION, y-INTERSECTION, x, y-INTERSECTION], "GREEN"]
        self.W_boundary = [[(x-INTERSECTION-int(INTERSECTION/2)), y-INTERSECTION, int(INTERSECTION/2), INTERSECTION], [x+INTERSECTION, y-INTERSECTION, x+INTERSECTION, y], "RED"]

    def get_status(self, direction):
        boundary_name = f"{direction}_boundary"
        cur_b = getattr(self, boundary_name, None)
        return cur_b[2]

    def break_distance(self, direction):
        if direction == "E":
            return self.E_boundary[1][0]
        elif direction == "W":
            return self.W_boundary[1][0]
        elif direction == "N":
            return self.N_boundary[1][1]
        elif direction == "S":
            return self.S_boundary[1][1]


    def update_status(self,direction, color):
        if direction == "E":
            self.E_boundary[2] = color


    def draw_section(self, cur_boundary):

        pygame.draw.rect(screen, WHITE, (cur_boundary[0][0], cur_boundary[0][1], cur_boundary[0][2], cur_boundary[0][3]))
        pygame.draw.line(screen, BLUE, (cur_boundary[1][0], cur_boundary[1][1]), (cur_boundary[1][2], cur_boundary[1][3]))
        pygame.draw.circle(screen, cur_boundary[2], ((cur_boundary[0][0] + cur_boundary[0][2]/2), (cur_boundary[0][1]+cur_boundary[0][3]/2)), 10)

    def draw(self):
        pygame.draw.circle(screen, GREEN, (self.x,self.y), 10)
        self.draw_section(self.N_boundary)
        self.draw_section(self.E_boundary)
        self.draw_section(self.S_boundary)
        self.draw_section(self.W_boundary)





class Car:
    # change to if stmt for x , y assignment based on direction
    def __init__(self, x, y, direction):
        self.speed = 10
        self.x = x
        self.y = y
        self.direction = direction
        self.breaking = False#remove
        self.accel = False



class Lane:

    def __init__(self, direction, start, light, pos, turn_direction): # width
        self.direction = direction
        self.offset = start
        self.horizontal_Cars = []
        self.vertical_Cars = []
        self.light = light  # can be array with direction
        self.pos = pos
        self.turn_direction = turn_direction
        self.left_dest_lane = None
        self.right_dest_lane = None


    def set_left_dest_lane(self, lane):
        self.left_dest_lane = lane

    def set_right_dest_lane(self, lane):
        self.right_dest_lane = lane

    def add_car(self, car):

        if car.direction == "E" or car.direction == "W":
            self.horizontal_Cars.append(car)
            self.horizontal_Cars.sort(key=lambda x: x.x, reverse=(car.direction == "W"))
        elif car.direction == "N" or car.direction == "S":
            self.vertical_Cars.append(car)
            self.vertical_Cars.sort(key=lambda x: x.y, reverse=(car.direction == "N"))



    def len_cars_ahead(self, car):
        if car.direction == "E" or car.direction == "W":
            cur_index = self.horizontal_Cars.index(car)
            if cur_index == len(self.horizontal_Cars) - 1:
                return GRID_SIZE*2
            else:
                distance = len(self.horizontal_Cars[cur_index:])*20
                return distance

        elif car.direction == "N" or car.direction == "S":
            cur_index = self.vertical_Cars.index(car)
            if cur_index == len(self.vertical_Cars) - 1:
                return GRID_SIZE*2
            else:
                distance = len(self.vertical_Cars[cur_index:])*20
                return distance


    def does_car_stop(self, car, direction):
        if direction == "E":
            return car.x >= self.light.break_distance("E") - self.len_cars_ahead(car)+GRID_SIZE and car.x <= self.light.x

        elif direction == "W":
            return car.x <= self.light.break_distance("W") + self.len_cars_ahead(car) - GRID_SIZE*2 and car.x >= self.light.x

        elif direction == "S":
            return car.y >= self.light.break_distance("S") - self.len_cars_ahead(car) + GRID_SIZE and car.y <= self.light.y

        elif direction == "N":
            return car.y <= self.light.break_distance("N") + self.len_cars_ahead(car) - GRID_SIZE*2 and car.y >= self.light.y






    def move_cars(self):

        for car in sorted(self.horizontal_Cars, key=lambda x: x.x):

            if self.pos == "E":
                if self.light.get_status("E") == "RED" and self.does_car_stop(car, "E"):
                    car.speed = 0
                    # make distance closer
                elif self.light.get_status("E") == "YELLOW" and self.does_car_stop(car, "E"):
                    car.speed = 10

                else:
                    car.speed = 10
                    if self.turn_direction == "left" and self.does_car_stop(car, "E"):
                        car.speed = 5
                        if car.x <= self.left_dest_lane.offset:
                            car.speed = 0
                            car.y = self.light.break_distance("N") - INTERSECTION*2
                            car.x = 0
                            car.direction = "N"
                            self.left_dest_lane.add_car(car)
                            self.horizontal_Cars.remove(car)
                            #might leave unanimated for now
                        else:
                            car.y -= car.speed

                    elif self.turn_direction == "right" and self.does_car_stop(car, "E"):
                        car.x = -GRID_SIZE
                        car.y = self.light.break_distance("S") + INTERSECTION*2
                        car.direction = "S"
                        self.right_dest_lane.add_car(car)
                        self.horizontal_Cars.remove(car)



                car.x += car.speed

            elif self.pos == "W":

                if self.does_car_stop(car, "W") and self.light.get_status("W") == "RED":
                    car.speed = 0

                elif self.light.get_status("W") == "YELLOW" and self.does_car_stop(car, "W"):
                    car.speed = 10

                else:
                    car.speed = 10
                    if self.turn_direction == "left" and self.does_car_stop(car, "W"):
                        car.speed = 5
                        if car.x >= self.left_dest_lane.offset:
                            car.speed = 0
                            car.y = self.light.break_distance("S") + INTERSECTION*2
                            car.x = 0
                            car.direction = "S"
                            self.left_dest_lane.add_car(car)
                            self.horizontal_Cars.remove(car)
                            #might leave unanimated for now
                        else:
                            car.y += car.speed

                    elif self.turn_direction == "right" and self.does_car_stop(car, "W"):
                        car.x = GRID_SIZE
                        car.y = self.light.break_distance("N") - INTERSECTION * 2
                        car.direction = "N"
                        self.right_dest_lane.add_car(car)
                        self.horizontal_Cars.remove(car)


                car.x -= car.speed

        for car in sorted(self.vertical_Cars, key=lambda y: y.y):

            if self.pos == "S":
                if self.light.get_status("S") == "RED" and self.does_car_stop(car, "S"):
                    car.speed = 0

                elif self.light.get_status("S") == "YELLOW" and self.does_car_stop(car, "S"):
                    car.speed = 10

                else:
                    car.speed = 10
                    if self.turn_direction == "left" and self.does_car_stop(car, "S"):
                        car.speed = 5
                        if car.y >= self.left_dest_lane.offset:
                            car.speed = 0
                            car.y = -7
                            car.x = self.light.break_distance("E") + INTERSECTION*2
                            car.direction = "E"
                            self.left_dest_lane.add_car(car)
                            self.vertical_Cars.remove(car)
                            car.speed = 8
                        else:
                            car.x += car.speed

                    elif self.turn_direction == "right" and self.does_car_stop(car, "S"):
                        car.x = self.light.break_distance("S") + INTERSECTION*2
                        car.y = -GRID_SIZE
                        car.direction = "W"
                        self.right_dest_lane.add_car(car)
                        self.vertical_Cars.remove(car)




                car.y += car.speed

            elif self.pos == "N":

                if self.light.get_status("N") == "RED" and self.does_car_stop(car, "N"):
                    car.speed = 0

                elif self.light.get_status("N") == "YELLOW" and self.does_car_stop(car, "N"):
                    car.speed = 10

                else:
                    car.speed = 10
                    if self.turn_direction == "left" and self.does_car_stop(car, "N"):
                        car.speed = 5
                        if car.y <= self.left_dest_lane.offset:
                            car.speed = 0
                            car.y = 0
                            car.x = self.light.break_distance("W") - INTERSECTION * 2 - GRID_SIZE
                            car.direction = "W"
                            self.left_dest_lane.add_car(car)
                            self.vertical_Cars.remove(car)
                        else:
                            car.x -= car.speed

                    elif self.turn_direction == "right" and self.does_car_stop(car, "N"):
                        car.x = self.light.break_distance("N") + INTERSECTION*2
                        car.y = GRID_SIZE
                        car.direction = "E"
                        self.right_dest_lane.add_car(car)
                        self.vertical_Cars.remove(car)

                car.y -= car.speed




    def draw(self):

        if self.direction == 'horizontal':
            for i in range(int(width / GRID_SIZE)):
                if i*GRID_SIZE < self.light.x - INTERSECTION or i*GRID_SIZE > self.light.x + INTERSECTION:
                    pygame.draw.rect(screen, WHITE, (i*GRID_SIZE, self.offset, GRID_SIZE, GRID_SIZE), width=1)

        if self.direction == 'vertical':
            for i in range(int(height / GRID_SIZE)):
                if i * GRID_SIZE < self.light.y - INTERSECTION or i * GRID_SIZE > self.light.y + INTERSECTION:
                    pygame.draw.rect(screen, WHITE, (self.offset, i*GRID_SIZE, GRID_SIZE, GRID_SIZE), width=1)

        for car in self.horizontal_Cars:
            pygame.draw.rect(screen, RED, (car.x, self.offset + car.y, GRID_SIZE, GRID_SIZE))

        for car in self.vertical_Cars:
            pygame.draw.rect(screen, RED, (self.offset + car.x, car.y, GRID_SIZE, GRID_SIZE))



def add_cars(lane, count):
    for i in range(count, 0, -1):
        car = Car(i*50, 0, "E")
        lane.add_car(car)


def add_cars2(lane, count):
    for i in range(count, 0, -1):
        car = Car(width - (i*50), 0, "W")
        lane.add_car(car)


def add_cars3(lane, count):
    for i in range(count):
        car = Car(0, i*50, "S")
        lane.add_car(car)

def add_cars4(lane, count):
    for i in range(count, 0, -1):
        car = Car(0, height - (i*50), "N")
        lane.add_car(car)


light1 = TrafficLight(width/2,height/2)

# get rid of direction base calculation off E / W, N / S
first = Lane("horizontal", 340, light1, "E", "right")
second = Lane("horizontal", 250, light1, "W", "right")
third = Lane("vertical", 350, light1, "S", "right")
fourth = Lane("vertical", 440, light1, "N", "right")

fourth.set_left_dest_lane(second)
third.set_left_dest_lane(first)
first.set_left_dest_lane(fourth)
second.set_left_dest_lane(third)

first.set_right_dest_lane(third)
second.set_right_dest_lane(fourth)
third.set_right_dest_lane(second)
fourth.set_right_dest_lane(first)


add_cars(first, 4)
add_cars2(second, 4)
add_cars3(third, 4)
add_cars4(fourth, 3)



clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                light1.update_status("E", "GREEN")

    screen.fill(BLACK)

    first.draw()
    second.draw()
    third.draw()
    fourth.draw()


    light1.draw()

    #pygame.draw.rect(screen,RED,(350,250,5,5))

    first.move_cars()
    second.move_cars()
    third.move_cars()
    fourth.move_cars()

    #pygame.time.wait(10)

    pygame.display.flip()
    clock.tick(20)

pygame.quit()
sys.exit()