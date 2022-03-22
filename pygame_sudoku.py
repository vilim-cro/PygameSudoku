import time
import pygame
import numpy

# Artificially slow down CPU when solving
slow_down_solving = True

# Initial state of the game
board1 = [[3, 0, 6, 5, 0, 8, 4, 0, 0],
        [5, 2, 0, 0, 0, 0, 0, 0, 0],
        [0, 8, 7, 0, 0, 0, 0, 3, 1],
        [0, 0, 3, 0, 1, 0, 0, 8, 0],
        [9, 0, 0, 8, 6, 3, 0, 0, 5],
        [0, 5, 0, 0, 9, 0, 6, 0, 0],
        [1, 3, 0, 0, 0, 0, 2, 5, 0],
        [0, 0, 0, 0, 0, 0, 0, 7, 4],
        [0, 0, 5, 2, 0, 6, 3, 0, 0]]

board = [[5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]]

class Square:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.domain = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        self.value = 0
        self.editable = True

    def __str__(self):
        return str(self.domain)

class Board:
    def __init__(self):
        self.board = board
        self.square_board = []
        self.assign_initial_numbers()

    def assign_map(self, g):
        self.g = g

    def assign_initial_numbers(self):
        # Appends empty squares in square_board
        for i in range(9):
            row = []
            for j in range(9):
                row.append(Square(i, j))
            self.square_board.append(row)

        # Assigns values to initial state
        for i in range(9):
            for j in range(9):
                value = self.board[i][j]
                if value != 0:
                    self.square_board[i][j].editable = False
                    self.assign(self.square_board[i][j], value, render=False)

    """ Removes a value from domain of all squares in 
    row, column and 3x3 field on the board"""
    def reduce_domain(self, row, column, value):
        removed = []
        index = column // 3 + row // 3 * 3
        for i in range(9):
            # Remove from rows
            square = self.square_board[row][i]
            if square.editable and value in square.domain and i != column:
                square.domain.remove(value)
                removed.append(i + 9 * row)
                if len(square.domain) == 0:
                    return False, removed

            # Remove from columns
            square = self.square_board[i][column]
            if square.editable and value in square.domain and i != row:
                square.domain.remove(value)
                removed.append(column + 9 * i)
                if len(square.domain) == 0:
                    return False, removed

            # Remove from big 3x3 squares
            x = i // 3 + (index // 3) * 3
            y = i % 3 + 3 * (index % 3)
            square = self.square_board[x][y]
            if square.editable and value in square.domain and (x != row or y != column):
                square.domain.remove(value)
                removed.append(y + 9 * x)
                if len(square.domain) == 0:
                    return False, removed
        return True, removed

    """Assigns a value to a object of Square class,
    removes assigned value from other square's domain in the row, column and 3x3 grid"""
    def assign(self, square, value, render=True):
        square.value = value
        if render:
            self.g.render()
        return self.reduce_domain(square.x, square.y, value)

    """Deassigns a value to a object of Square class,
    adds deassigned value to other square's domain in the row, column and 3x3 grid"""
    def deassign(self, square, value, list):
        square.value = 0
        self.g.render()
        for index in list:
            x = index // 9
            y = index % 9
            if self.square_board[x][y].editable:
                self.square_board[x][y].domain.add(value)

class Graphics:
    def __init__(self, board):
        self.map_width = 810
        self.map_height = 810
        self.screen = pygame.display.set_mode([self.map_width, self.map_height])
        self.map_color = (255, 255, 255)
        self.map = pygame.Rect(810, 810, 810, 810)
        self.map.topleft = (0,0)
        self.square_width = self.map_width // 9 # Because the grid is 9x9
        self.line_color = (0, 0, 0) # Black lines
        self.selected_x, self.selected_y = 0, 0 # Saves the point user clicked on
        self.b = board

    # Draws GUI
    def render(self):
        # Draw map and map border
        pygame.draw.rect(surface=self.screen, color=self.map_color, rect=self.map)
        pygame.draw.rect(surface=self.screen, color=self.line_color, rect=self.map, width=3)

        # Draw sudoku grid (9x9)
        for i in range(8):
            width = 1
            if (i + 1) % 3 == 0:
                width = 3
            pygame.draw.line(surface=self.screen, color=self.line_color,
            start_pos=(0, self.square_width * (i + 1)), end_pos=(self.map_height, self.square_width * (i + 1)), 
            width=width)
        for i in range(8):
            width = 1
            if (i + 1) % 3 == 0:
                width = 3
            pygame.draw.line(surface=self.screen, color=self.line_color,
            start_pos=(self.square_width * (i + 1), 0), end_pos=(self.square_width * (i + 1), self.map_height), 
            width=width)

        self.fill_numbers() # Fills initial numbers on the board
        pygame.display.flip()


    # Writes(blits) numbers from board matrix into GUI
    def fill_numbers(self):
        f = pygame.font.SysFont('Arial', 30) # Defines font type and size
        for i in range(9):
            for j in range(9):
                number = self.b.square_board[i][j].value
                if number != 0:
                    img = f.render(str(number), True, self.line_color)
                    self.screen.blit(img, (40 + self.square_width * j, 30 + self.square_width * i))

# Removes all characters in data from a set
def clean(set, data):
    for d in data:
        if d in set:
            set.remove(d)

# Checks whether every row, column and big 3x3 squares have all numbers 1-9 in them
def check_if_solved(b):
    rows = [set() for i in range(9)]
    columns = [set() for i in range(9)]
    grids = [set() for i in range(9)]

    # Fills empty sets with board values
    for i in range(9):
        for j in range(9):
            rows[i].add(b.square_board[i][j].value)
            columns[i].add(b.square_board[j][i].value)
            x = j // 3 + (i // 3) * 3
            y = j % 3 + 3 * (i % 3)
            grids[i].add(b.square_board[x][y].value)
    
    """Loops over all sets, removes empty values from them and 
    determines whether all elements are in it (whether len is 9)"""
    for i in range(9):
        clean(rows[i], ["", 0])
        clean(columns[i], ["", 0])
        clean(grids[i], ["", 0])
        if len(rows[i]) != 9 or len(columns[i]) != 9 or len(grids[i]) != 9:
            return False
    return True

# Starts a game, enters a repeated loop until the problem is solved
def start_game():
    pygame.init()
    b = Board()
    g = Graphics(b)
    b.assign_map(g) # Adds Graphics object g to Board object b

    running = True
    while running:
        for event in pygame.event.get():
            # Checks whether the user has exited
            if event.type == pygame.QUIT:
                running = False
            # Stores (x, y) coordinates of the square the user clicked on
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                g.selected_x = y // g.square_width
                g.selected_y = x // g.square_width
            # Changes the board value depending on the key pressed and sqaure clicked
            if event.type == pygame.KEYDOWN:
                selected_square = b.square_board[g.selected_x][g.selected_y]
                if event.key == pygame.K_1 and selected_square.editable:
                    selected_square.value = 1
                elif event.key == pygame.K_2 and selected_square.editable:
                    selected_square.value = 2
                elif event.key == pygame.K_3 and selected_square.editable:
                    selected_square.value = 3
                elif event.key == pygame.K_4 and selected_square.editable:
                    selected_square.value = 4
                elif event.key == pygame.K_5 and selected_square.editable:
                    selected_square.value = 5
                elif event.key == pygame.K_6 and selected_square.editable:
                    selected_square.value = 6
                elif event.key == pygame.K_7 and selected_square.editable:
                    selected_square.value = 7
                elif event.key == pygame.K_8 and selected_square.editable:
                    selected_square.value = 8
                elif event.key == pygame.K_9 and selected_square.editable:
                    selected_square.value = 9
                elif event.key == pygame.K_DELETE and selected_square.editable:
                    selected_square.value = ""  # Clears value if DEL key is clicked
                elif event.key == pygame.K_s:   # s key is for solve
                    solve(b)
                if check_if_solved(b):
                    g.render()
                    time.sleep(5) # Wait 5 secs then close window
                    running = False
        g.render()

    pygame.quit()

# Sets all editable values on the board to 0
def clear_board(b):
    for i in range(9):
        for j in range(9):
            if b.square_board[i][j].editable:
                b.square_board[i][j].value = 0

# Makes a list of unassigned square objects and sorts them by length of their domain
def make_sorted_square_list(b):
    sq = list(numpy.concatenate(b.square_board)) # Converts matrix to 1D list
    sq.sort(key = lambda x: len(x.domain)) # Sorts a list by the length of its domain
    squares = []    # Makes a list of unassigned squares 
    for s in sq:
        if s.value == 0:
            squares.append(s)
    return squares

# Recursivly calls itself until the problem i solved
def backtrack(b, squares):
    """If there are no more squares that need assigning,
    then the problem is solved"""
    """If there exists an unassigned square with empty domain,
    some value was wrongly assigned, need to go back"""
    if len(squares) == 0:
        return squares
    elif len(squares[0].domain) == 0:
        return None

    squares = make_sorted_square_list(b)
    square = squares.pop(0) # Gets the square with smallest domain
    for value in square.domain:
        if slow_down_solving:
            time.sleep(0.1)     # Slow down CPU solving
        success, removed_indexes = b.assign(square, value)  # Try a value from square domain
        if success:
            result = backtrack(b, squares)  # If success, keep assigning
            if result != None:
                return result
        square.deassign(value, removed_indexes)     # Otherwise, deassign value
    return None

def solve(b):
    clear_board(b)  # Clears board values before anything else
    squares = make_sorted_square_list(b)
    print(backtrack(b, squares))

if __name__== "__main__":
    start_game()