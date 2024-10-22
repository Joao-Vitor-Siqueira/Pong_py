from dataclasses import field

from blessed.terminal import Terminal
from six import print_


class Pong:
    def __init__(self,width,height,theme):
        #Assets
        self.__term = Terminal()
        self.__width = width
        self.__height = height
        self.half_x = int(self.__width / 2)
        self.half_y = int(self.__height / 2)

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


        #Config
        self.__theme = theme
        self.__themes = (("red","darkgreen","darkblue"),("white","black","white"))


    def init_field(self):
        return

    def print_in_color(self,color, x, y):
        color_method = getattr(self.__term, color, self.__term.white)
        print(self.__term.move_xy(x,y) + color_method("\u2588"), end="")

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
                    self.print_in_color("black", x, y)

                else:
                    self.print_in_color(self.__themes[self.__theme][1],x,y)


                if x == self.__width - 1:
                    print()


    def play(self):
        #listen for input

        #printField

        #moveBall

        return