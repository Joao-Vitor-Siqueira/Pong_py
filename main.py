from blessed.terminal import Terminal

term = Terminal()

for i in range(12):
    print(term.move_xy(i,1) + term.red("XD"))


    