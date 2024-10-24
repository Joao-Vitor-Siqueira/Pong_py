from blessed.terminal import Terminal
import time
import threading
from pong.input_listener.input_listener_factory import InputListenerFactory


def get_opposite_key(key):
    if key == "'W'":
        return "'S'"
    elif key == "'S'":
        return  "'W'"
    elif key == 'KEY.UP':
        return 'KEY.DOWN'
    else:
        return 'KEY.UP'


class Pong:
    def __init__(self,width,height,theme,score):
        #Config
        self.__width = width
        self.__height = height
        self.half_x = int(self.__width / 2)
        self.half_y = int(self.__height / 2)
        self.__theme = theme
        self.__themes = (("red", "darkgreen", "darkblue", "black"), ("white", "black", "white", "darkgray"))
        self.__targetScore = score

        #Game Entities
        self.__term = Terminal()
        self.__field = [["\u2588" for x in range(self.__width)] for y in range(self.__height)]
        self.__ball_pos = {"y": self.half_y, "x": [self.half_x, self.half_x - 1]}

        self.__player1_pos = {
                    "y": [ self.half_y - 1, self.half_y, self.half_y + 1],
                    "x": [4, 5]
                    }
        self.__player2_pos = {
            "y": [ self.half_y - 1, self.half_y, self.half_y + 1],
            "x": [self.__width - 5, self.__width - 6]
                    }

        #Game Logic
        self.__gameOver = False
        self.__player1_score = 0
        self.__player2_score = 0

        self.__input_buffer = []
        self.__field_changes = []


        self.__directions = {
            "upRight": (-1, 1),
            "upLeft": (-1, -1),
            "downRight": (1, 1),
            "downLeft": (1, -1),
        }
        self.__ball_direction = [-1 ,1]

        #Threads
        self.__input_listener = InputListenerFactory().get_listener()
        self.__input_handler = threading.Thread(target=self.handle_input)
        self.__ball = threading.Thread(target=self.move_ball)

    def print_in_color(self,color, x, y,val = "\u2588"):
        color_method = getattr(self.__term, color, self.__term.white)
        print(self.__term.move_xy(x,y) + color_method(val), end="")

    def is_player(self,x,y):
        return x in self.__player1_pos["x"] and y in self.__player1_pos["y"] or x in self.__player2_pos["x"] and y in self.__player2_pos["y"]


    def render_field(self):
        for y in range(self.__height):
            for x in range(self.__width):

                if y == self.__ball_pos["y"] and x in self.__ball_pos["x"]:
                    self.print_in_color(self.__themes[self.__theme][0], x, y)

                elif self.is_player(x,y):
                    self.print_in_color(self.__themes[self.__theme][2], x, y)

                elif y == 0 or y == self.__height - 1 or x <= 1 or x >= self.__width - 2:
                    self.print_in_color(self.__themes[self.__theme][3],x,y)

                else:
                    self.print_in_color(self.__themes[self.__theme][1],x,y)


                if x == self.__width - 1:
                    print()

    def update_field(self):
        for pos in self.__field_changes:
            y = pos[0]
            x = pos[1]
            if y == self.__ball_pos["y"] and x in self.__ball_pos["x"]:
                self.print_in_color(self.__themes[self.__theme][0], x, y)

            elif self.is_player(x, y):
                self.print_in_color(self.__themes[self.__theme][2], x, y)

            elif y == 0 or y == self.__height - 1 or x <= 1 or x >= self.__width - 2:
                self.print_in_color(self.__themes[self.__theme][3], x, y)

            else:
                self.print_in_color(self.__themes[self.__theme][1], x, y)

        self.__field_changes = []

    def move_ball(self):
        while not self.__gameOver:
            time.sleep(0.075)

            next_y = self.__ball_pos["y"] + self.__ball_direction[0]
            next_x = [self.__ball_pos["x"][0] + self.__ball_direction[1], self.__ball_pos["x"][1] + self.__ball_direction[1]]

            if self.check_collision(next_x,next_y):
                if next_y == 0 or next_y == self.__height - 1:
                    self.invert_direction(0)
                else:
                    self.invert_direction(1)
                next_y = self.__ball_pos["y"] + self.__ball_direction[0]
                next_x = [self.__ball_pos["x"][0] + self.__ball_direction[1], self.__ball_pos["x"][1] + self.__ball_direction[1]]

            for i in range(2):
                self.__field_changes.append((next_y, next_x[i]))
                self.__field_changes.append((self.__ball_pos["y"], self.__ball_pos["x"][i]))
            self.__ball_pos["y"] = next_y
            self.__ball_pos["x"] = next_x

    def check_collision(self,x,y):
        if y == 0 or y == self.__height - 1:
            return True
        for val in x:
            if val < 2 or val > self.__width - 3:
                return  True

            if self.is_player(val,y):
                return True

        return False

    def invert_direction(self,index):
        if self.__ball_direction[index] < 0:
            self.__ball_direction[index] = abs(self.__ball_direction[index])
        else:
            self.__ball_direction[index] = -abs(self.__ball_direction[index])

    def reset_ball(self):
        self.__ball_pos = {"y": self.half_y, "x": [self.half_x, self.half_x - 1]}


    def handle_input(self):
        while not self.__gameOver:
            time.sleep(0.15)

            if not self.__input_listener.empty():

                if self.__input_listener.find("'W'") and self.is_valid(self.__player2_pos["y"][0]):
                    self.move_paddle(0, 2)

                if self.__input_listener.find("'S'")  and self.is_valid(self.__player2_pos["y"][-1]):
                    self.move_paddle(1, 2)

                if  self.__input_listener.find('KEY.UP') and self.is_valid(self.__player1_pos["y"][0]):
                    self.move_paddle(0, 1)

                if  self.__input_listener.find('KEY.DOWN') and self.is_valid(self.__player1_pos["y"][-1]):
                    self.move_paddle(1, 1)


    def is_valid(self,y):
        return 1 < y < self.__height - 2

    def move_paddle(self, direction, player):
        new_pos = []

        if player == 1:
            for i in range(len(self.__player1_pos["y"])):
                if direction == 0:
                    new_pos.append(self.__player1_pos["y"][i] - 1)
                else:
                    new_pos.append(self.__player1_pos["y"][i] + 1)
                self.__field_changes.append((self.__player1_pos["y"][i], 4))
                self.__field_changes.append((self.__player1_pos["y"][i], 5))
                self.__field_changes.append((new_pos[i], 4))
                self.__field_changes.append((new_pos[i], 5))

            self.__player1_pos["y"] = new_pos

        else:
            for i in range(len(self.__player2_pos["y"])):
                if direction == 0:
                    new_pos.append(self.__player2_pos["y"][i] - 1)
                else:
                    new_pos.append(self.__player2_pos["y"][i] + 1)
                self.__field_changes.append((self.__player2_pos["y"][i], self.__width - 5))
                self.__field_changes.append((self.__player2_pos["y"][i], self.__width - 6))
                self.__field_changes.append((new_pos[i], self.__width - 5))
                self.__field_changes.append((new_pos[i], self.__width - 6))

            self.__player2_pos["y"] = new_pos




    def play(self):

        self.__input_listener.start()
        self.__input_handler.start()
        self.__ball.start()

        with self.__term.cbreak(), self.__term.hidden_cursor():

            print(self.__term.home + self.__term.clear())
            self.render_field()

            while not self.__gameOver:
                self.update_field()

                if 2 in self.__ball_pos["x"]:
                    self.__player2_score += 1
                    time.sleep(1.5)
                    self.reset_ball()

                elif self.__width - 3 in self.__ball_pos["x"]:
                    self.__player1_score += 1
                    time.sleep(1.5)
                    self.reset_ball()


                self.print_in_color("white",self.__width + 10,self.half_y - 1,"Player 1: " + str(self.__player1_score))
                self.print_in_color("white",self.__width + 10,self.half_y + 1,"Player 2: " + str(self.__player2_score))




                if self.__player1_score == self.__targetScore or self.__player2_score == self.__targetScore:
                    self.__gameOver = True
                    print(self.__term.home + self.__term.clear())
                    self.__input_handler.join()
                    self.__ball.join()
                    self.__input_listener.join()

                    winner = "Player 1" if self.__player1_score > self.__player2_score else "Player 2"

                    self.print_in_color("white",0,0,f"{winner} wins!\n")











