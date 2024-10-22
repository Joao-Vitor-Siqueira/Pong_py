from queue import Queue

from blessed.terminal import Terminal
import time
import threading
import queue


class Pong:
    def __init__(self,width,height,theme):
        #Config
        self.__width = width
        self.__height = height
        self.half_x = int(self.__width / 2)
        self.half_y = int(self.__height / 2)
        self.__theme = theme
        self.__themes = (("red", "darkgreen", "darkblue", "black"), ("white", "black", "white", "darkgray"))
        self.__targetScore = 5
        self.__input_buffer = Queue()

        #Game Entities
        self.__term = Terminal()
        self.__field = [["\u2588" for x in range(self.__width)] for y in range(self.__height)]
        self.__ball = {"y": self.half_y, "x": [self.half_x,self.half_x - 1]}

        self.__player1 = {
                    "y": [self.half_y - 2, self.half_y - 1, self.half_y, self.half_y + 1, self.half_y + 2],
                    "x": [4, 5]
                    }
        self.__player2 = {
            "y": [self.half_y - 2, self.half_y - 1, self.half_y, self.half_y + 1, self.half_y + 2],
            "x": [self.__width - 5, self.__width - 6]
                    }

        #Game Logic
        self.__gameOver = False
        self.__player1_score = 0
        self.__player2_score = 0


        self.__directions = {
            "upRight": (-1, 1),
            "upLeft": (-1, -1),
            "downRight": (1, 1),
            "downLeft": (1, -1),
        }
        self.__ball_direction = [-1 ,1]


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

    def move_ball(self):
        while not self.__gameOver:
            time.sleep(0.15)

            nextY = self.__ball["y"] + self.__ball_direction[0]
            nextX = [self.__ball["x"][0] + self.__ball_direction[1],self.__ball["x"][1] + self.__ball_direction[1]]

            if self.check_collision(nextX,nextY):
                if nextY == 0 or nextY == self.__height - 1:
                    self.invert_direction(0)
                else:
                    self.invert_direction(1)
                nextY = self.__ball["y"] + self.__ball_direction[0]
                nextX = [self.__ball["x"][0] + self.__ball_direction[1], self.__ball["x"][1] + self.__ball_direction[1]]

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

    def listen_input(self):
        while not self.__gameOver:
            val = self.__term.inkey()
            self.__input_buffer.put(val)



    def player1_input_listener(self):
        while not self.__gameOver:
            try:
                val = self.__input_buffer.get(block=False)

                if val.upper() == "W" and self.is_valid(self.__player2["y"][0]):
                    self.move_paddle(0, 2)

                elif val.upper() == "S" and self.is_valid(self.__player2["y"][4]):
                    self.move_paddle(1, 2)
            except:
                continue

    def player2_input_listener(self):
        while not self.__gameOver:
            try:
                val = self.__input_buffer.get(block=False)

                if val.upper() == "O" and self.is_valid(self.__player1["y"][0]):
                    self.move_paddle(0, 1)

                elif val.upper() == "L" and self.is_valid(self.__player1["y"][4]):
                    self.move_paddle(1, 1)
            except:
                continue

    def is_valid(self,y):
        return 1 < y < self.__height - 2

    def move_paddle(self, direction, player):
        if player == 1:
            for i in range(len(self.__player1["y"])):
                if direction == 0:
                    self.__player1["y"][i] -= 1
                else:
                    self.__player1["y"][i] += 1
        else:
            for i in range(len(self.__player2["y"])):
                if direction == 0:
                    self.__player2["y"][i] -= 1
                else:
                    self.__player2["y"][i] += 1

    def play(self):

        input_listener = threading.Thread(target=self.listen_input)
        player1 = threading.Thread(target=self.player1_input_listener)
        player2 = threading.Thread(target=self.player2_input_listener)
        ball = threading.Thread(target=self.move_ball)

        input_listener.start()
        player1.start()
        player2.start()
        ball.start()

        with self.__term.cbreak(), self.__term.hidden_cursor():
            print(self.__term.home + self.__term.clear())

            while not self.__gameOver:


                self.print_field()


                if 2 in self.__ball["x"]:
                    self.__player2_score += 1
                    time.sleep(1.5)
                    self.reset_ball()

                elif self.__width - 3 in self.__ball["x"]:
                    self.__player1_score += 1
                    time.sleep(1.5)
                    self.reset_ball()


                self.print_in_color("white",self.__width + 10,self.half_y,str(self.__player1_score))
                self.print_in_color("white",self.__width + 20,self.half_y,str(self.__player2_score))



                if self.__player1_score == self.__targetScore or self.__player2_score == self.__targetScore:
                    self.__gameOver = True
                    print(self.__term.home + self.__term.clear())
                    player1.join()
                    player2.join()
                    ball.join()
                    input_listener.join()





