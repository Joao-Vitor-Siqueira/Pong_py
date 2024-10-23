from blessed.terminal import Terminal
import time
import threading
from pynput.keyboard import Key, Listener


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
        self.__ball = {"y": self.half_y, "x": [self.half_x,self.half_x - 1]}

        self.__player1 = {
                    "y": [ self.half_y - 1, self.half_y, self.half_y + 1],
                    "x": [4, 5]
                    }
        self.__player2 = {
            "y": [ self.half_y - 1, self.half_y, self.half_y + 1],
            "x": [self.__width - 5, self.__width - 6]
                    }

        #Game Logic
        self.__gameOver = False
        self.__player1_score = 0
        self.__player2_score = 0

        self.__input_buffer = []

        self.__changes = []


        self.__directions = {
            "upRight": (-1, 1),
            "upLeft": (-1, -1),
            "downRight": (1, 1),
            "downLeft": (1, -1),
        }
        self.__ball_direction = [-1 ,1]


    def log(self):
        return str(self.__input_buffer)

    def print_in_color(self,color, x, y,val = "\u2588"):
        color_method = getattr(self.__term, color, self.__term.white)
        print(self.__term.move_xy(x,y) + color_method(val), end="")

    def is_player(self,x,y):
        return x in self.__player1["x"] and y in self.__player1["y"] or x in self.__player2["x"] and y in self.__player2["y"]

    def print_field(self):
        for y in range(self.__height):
            for x in range(self.__width):

                if y == self.__ball["y"] and x in self.__ball["x"]:
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
        for pos in self.__changes:
            y = pos[0]
            x = pos[1]
            if y == self.__ball["y"] and x in self.__ball["x"]:
                self.print_in_color(self.__themes[self.__theme][0], x, y)

            elif self.is_player(x, y):
                self.print_in_color(self.__themes[self.__theme][2], x, y)

            elif y == 0 or y == self.__height - 1 or x <= 1 or x >= self.__width - 2:
                self.print_in_color(self.__themes[self.__theme][3], x, y)

            else:
                self.print_in_color(self.__themes[self.__theme][1], x, y)


    def move_ball(self):
        while not self.__gameOver:
            time.sleep(0.075)

            nextY = self.__ball["y"] + self.__ball_direction[0]
            nextX = [self.__ball["x"][0] + self.__ball_direction[1],self.__ball["x"][1] + self.__ball_direction[1]]

            if self.check_collision(nextX,nextY):
                if nextY == 0 or nextY == self.__height - 1:
                    self.invert_direction(0)
                else:
                    self.invert_direction(1)
                nextY = self.__ball["y"] + self.__ball_direction[0]
                nextX = [self.__ball["x"][0] + self.__ball_direction[1], self.__ball["x"][1] + self.__ball_direction[1]]

            for i in range(2):
                self.__changes.append((nextY,nextX[i]))
                self.__changes.append((self.__ball["y"],self.__ball["x"][i]))

            self.__ball["y"] = nextY
            self.__ball["x"] = nextX

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
        self.__ball = {"y": self.half_y, "x": [self.half_x, self.half_x - 1]}

    def listen_key_press(self,key):

        if not isinstance(key, str):
            key = str(key).upper()

        if (
            key in ("'W'","'S'",'KEY.UP','KEY.DOWN') and key not in self.__input_buffer and
            not get_opposite_key(key) in self.__input_buffer
        ):
                self.__input_buffer.append(key)

    def listen_key_release(self,key):
        if not isinstance(key, str):
            key = str(key).upper()

        if key in self.__input_buffer:
            self.__input_buffer.pop(self.__input_buffer.index(key))

    def handle_input(self):
        while not self.__gameOver:

            time.sleep(0.15)
            if len(self.__input_buffer):

                if "'W'" in self.__input_buffer and self.is_valid(self.__player2["y"][0]):
                    self.move_paddle(0, 2)
                if "'S'" in self.__input_buffer  and self.is_valid(self.__player2["y"][-1]):
                    self.move_paddle(1, 2)
                if  'KEY.UP' in self.__input_buffer and self.is_valid(self.__player1["y"][0]):
                    self.move_paddle(0, 1)
                if  'KEY.DOWN' in self.__input_buffer and self.is_valid(self.__player1["y"][-1]):
                    self.move_paddle(1, 1)

    def is_valid(self,y):
        return 1 < y < self.__height - 2

    def move_paddle(self, direction, player):
        new_pos = []

        if player == 1:
            for i in range(len(self.__player1["y"])):
                if direction == 0:
                    new_pos.append(self.__player1["y"][i] - 1)
                else:
                    new_pos.append(self.__player1["y"][i] + 1)
                self.__changes.append((self.__player1["y"][i], 4))
                self.__changes.append((self.__player1["y"][i], 5))
                self.__changes.append((new_pos[i],4))
                self.__changes.append((new_pos[i], 5))

            self.__player1["y"] = new_pos

        else:
            for i in range(len(self.__player2["y"])):
                if direction == 0:
                    new_pos.append(self.__player2["y"][i] - 1)
                else:
                    new_pos.append(self.__player2["y"][i] + 1)
                self.__changes.append((self.__player2["y"][i], self.__width - 5))
                self.__changes.append((self.__player2["y"][i], self.__width - 6))
                self.__changes.append((new_pos[i], self.__width - 5))
                self.__changes.append((new_pos[i], self.__width - 6))

            self.__player2["y"] = new_pos




    def play(self):

        input_listener = Listener(on_press=self.listen_key_press,on_release=self.listen_key_release)
        input_handler = threading.Thread(target=self.handle_input)
        ball = threading.Thread(target=self.move_ball)

        input_listener.start()
        input_handler.start()
        ball.start()

        with self.__term.cbreak(), self.__term.hidden_cursor():
            print(self.__term.home + self.__term.clear())
            self.print_field()

            while not self.__gameOver:
                self.update_field()

                if 2 in self.__ball["x"]:
                    self.__player2_score += 1
                    time.sleep(1.5)
                    self.reset_ball()

                elif self.__width - 3 in self.__ball["x"]:
                    self.__player1_score += 1
                    time.sleep(1.5)
                    self.reset_ball()


                self.print_in_color("white",self.__width + 10,self.half_y - 1,"Player 1: " + str(self.__player1_score))
                self.print_in_color("white",self.__width + 10,self.half_y + 1,"Player 2: " + str(self.__player2_score))


                if self.__player1_score == self.__targetScore or self.__player2_score == self.__targetScore:
                    self.__gameOver = True
                    print(self.__term.home + self.__term.clear())
                    input_handler.join()
                    ball.join()
                    input_listener.join(timeout=0.15)







