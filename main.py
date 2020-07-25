import math
import pygame, time
import random

# minPQ for puzzle boards
class MinPQ:
    def __init__(self):
        self.array = [None]
        self.waiting_dict = {}
        self.obj_array = []
        self.size = 0
        self.minVal = None

    def swap_pos(self, pos_a, pos_b):
        self.array[pos_a], self.array[pos_b] = self.array[pos_b], self.array[pos_a]

    def swim(self, cur_pos):
        while 1 < cur_pos <= self.size:
            parent_nod = cur_pos // 2
            if self.array[parent_nod].element > self.array[cur_pos].element:
                self.swap_pos(parent_nod, cur_pos)
                cur_pos = parent_nod
            else:
                break

    def sink(self, cur_pos):
        while cur_pos <= self.size // 2:
            child_nod = cur_pos * 2
            if (child_nod == self.size or self.array[child_nod].element <= self.array[child_nod + 1].element) and \
                    self.array[child_nod].element < self.array[cur_pos].element:
                self.swap_pos(child_nod, cur_pos)
                cur_pos = child_nod
            elif child_nod != self.size and self.array[child_nod].element > self.array[child_nod + 1].element and \
                    self.array[child_nod + 1].element < self.array[cur_pos].element:
                self.swap_pos(child_nod + 1, cur_pos)
                cur_pos = child_nod + 1
            else:
                break

    def insert(self, board):
        value = board.manhattan() + board.cost
        tmp_board = board
        tmp_element = self.Pair(tmp_board, value, board.manhattan(), board.cost)

        if self.size == 0:
            self.size = 1
            self.array.append(tmp_element)
            self.minVal = self.array[1]
        else:
            self.size += 1
            self.array.append(tmp_element)
            self.swim(self.size)

    def get(self):
        if self.size == 0:
            raise Exception("empty heap")
        return self.array[1].obj

    def remove(self):
        if self.size == 0:
            return -1
        tmp_board = self.array[1].obj
        self.swap_pos(1, self.size)
        self.array.pop()
        self.size -= 1
        self.sink(1)
        return tmp_board

    def draw_heap(self):
        if self.size < 1:
            return 0
        level = int(math.log(self.size, 2)) + 1
        total = 0
        for i in range(level):
            gap = total
            total = int(math.pow(2, level - i - 1)) - 1
            row_count = int(math.pow(2, i))
            print(" " * total, end='')
            for j in range(row_count, row_count * 2):
                if j > self.size:
                    break
                print(self.array[j], ' ' * gap, sep='', end='')
            print()

    # def drawFull(self):
    #     if self.size < 1:
    #         return 0
    #     i = 0
    #     print("To be seen(from PQ class)")
    #     for val in self.array:
    #         if val is None:
    #             continue
    #         print(f">>> ToBe - {i} <<<")
    #         bord = val.obj
    #         print("prority >> ", val.element)
    #         bord.to_string()
    #         i += 1

    class Pair:
        def __init__(self, obj, element, dist, cost):
            self.obj = obj
            self.element = element
            self.cost = cost
            self.dist = dist


class Board:
    def __init__(self, rows, cols, array):
        self.rows = rows
        self.cols = cols
        self.array = self.copy(array)
        self.last_direction = None
        self.cost = 0
        self.path = []
        self.goal = [[j * self.cols + i + 1 for i in range(cols)] for j in range(rows)]
        self.goal[rows - 1][cols - 1] = None
        self.manhattan_array = [None]
        self.manhattan_dist = self.manhattan(firstTime=True)
        self.hamming_dist = self.hamming(firstTime=True)
        self.neighbours_list = []
        self.priority = self.manhattan_dist + self.cost

    def copy(self, old_list):
        r = len(old_list)
        c = len(old_list[0])
        new_list = [[element for element in sub_list] for sub_list in old_list]
        return new_list

    # def to_string(self):
    #     print('---' * self.rows)
    #     for row in range(self.rows):
    #         for col in range(self.cols):
    #             item = self.array[row][col]
    #             if item is not None:
    #                 print(item, end=' ')
    #             else:
    #                 print(" ", end=' ')
    #         print()
    #     print("Manahattan Dist:", self.manhattan_dist, "moves :", self.cost, "last_direction :", self.last_direction,
    #           "neighbour count :", len(self.neighbours_list))
    #     print('---' * self.rows)

    def get_dimension(self, element, goal=False):

        if goal:
            for row in range(self.rows):
                try:
                    col = self.goal[row].index(element)
                    return row, col
                except:
                    continue
        else:
            for row in range(self.rows):
                try:
                    col = self.array[row].index(element)
                    return row, col
                except:
                    continue

        raise Exception(f"Element-{element} not found in the board")

    def manhattan(self, firstTime=True):
        if firstTime:
            tmp = 0
            for row in range(self.rows):
                for col in range(self.cols):
                    if row == self.rows - 1 and col == self.cols - 1:
                        return tmp
                    item = row * self.cols + col + 1
                    rowx, colx = self.get_dimension(item)
                    tmp_x = abs(rowx - row) + abs(colx - col)
                    self.manhattan_array.append(tmp_x)
                    tmp += tmp_x

    def hamming(self, firstTime=False):
        hamming_dist = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if row == self.rows - 1 and col == self.cols - 1:
                    if firstTime:
                        return hamming_dist
                    else:
                        self.hamming_dist = hamming_dist
                else:
                    if self.goal[row][col] == self.array[row][col]:
                        continue
                    else:
                        hamming_dist += 1

    def is_equals(self, obj):
        if self.array == obj.array:
            return True
        return False

    def get_neighbours(self):
        row_blank, col_blank = self.get_dimension(None)
        neighbour_count = 0
        left = "left"
        right = "right"
        up = "up"
        down = "down"
        neighbour_array = []
        if row_blank == 0:
            neighbour_array.append(down)
            if col_blank == 0:
                neighbour_count = 2
                neighbour_array.append(right)
            elif col_blank == self.cols - 1:
                neighbour_count = 2
                neighbour_array.append(left)
            else:
                neighbour_count = 3
                neighbour_array.append(left)
                neighbour_array.append(right)
        elif row_blank == self.rows - 1:
            neighbour_array.append(up)
            if col_blank == 0:
                neighbour_count = 2
                neighbour_array.append(right)
            elif col_blank == self.cols - 1:
                neighbour_count = 2
                neighbour_array.append(left)
            else:
                neighbour_count = 3
                neighbour_array.append(left)
                neighbour_array.append(right)
        elif col_blank == 0:
            neighbour_count = 3
            neighbour_array.append(up)
            neighbour_array.append(right)
            neighbour_array.append(down)
        elif col_blank == self.cols - 1:
            neighbour_count = 3
            neighbour_array.append(left)
            neighbour_array.append(up)
            neighbour_array.append(down)
        else:
            neighbour_count = 4
            neighbour_array.append(left)
            neighbour_array.append(right)
            neighbour_array.append(up)
            neighbour_array.append(down)
        return neighbour_count, neighbour_array

    def swap_by_index(self, point_a, point_b):
        x0, y0 = point_a
        x1, y1 = point_b
        arr = self.array
        arr[x0][y0], arr[x1][y1] = arr[x1][y1], arr[x0][y0]
        return arr

    def move_to(self, direction):
        row_none, col_none = self.get_dimension(None)
        block = row_none, col_none
        self.last_direction = direction
        if direction == "left":
            self.swap_by_index(block, [row_none, col_none - 1])
        elif direction == "right":
            self.swap_by_index(block, [row_none, col_none + 1])
        elif direction == "up":
            self.swap_by_index(block, [row_none - 1, col_none])
        elif direction == "down":
            self.swap_by_index(block, [row_none + 1, col_none])
        else:
            print("direction :", direction)
            raise Exception("Direction of block is INVALID")

    def neighbours(self, lastdirection=None):
        neighbour_count, old_neighbours = self.get_neighbours()
        moves = self.cost + 1
        tmp_path = [path for path in self.path]
        tmp_path.append(self.last_direction)
        if lastdirection is not None:
            if lastdirection == "left":
                lastdirection = "right"
            elif lastdirection == "right":
                lastdirection = "left"
            elif lastdirection == "up":
                lastdirection = "down"
            elif lastdirection == "down":
                lastdirection = "up"
        if lastdirection in old_neighbours:
            old_neighbours.remove(lastdirection)
            neighbour_count -= 1
        new_neighbours = [None for _ in range(neighbour_count)]
        for i in range(neighbour_count):
            new_neighbours[i] = Board(self.rows, self.cols, self.array)
            new_neighbours[i].move_to(old_neighbours[i])
            new_neighbours[i].cost = moves
            new_neighbours[i].path = tmp_path
        self.neighbours_list = new_neighbours[:]
        return self.neighbours_list

    def is_goal(self):
        if self.array == self.goal:
            return True
        return False

    def get_inversions(self):
        # convert puzzle to plane
        plane_array = []
        for row in range(self.rows):
            for col in range(self.cols):
                val = self.array[row][col]
                if val is not None:
                    plane_array.append(val)

        inv_count = 0
        n = len(plane_array)
        for i in range(n - 1):
            for j in range(i + 1, n):
                if (plane_array[i] > plane_array[j]):
                    inv_count += 1

        return inv_count

    # // is the initial board solvable? (see below)
    def isSolvable(self):
        inversions = self.get_inversions()
        n = self.rows
        if n % 2 and inversions % 2 == 0:
            return True
        if n % 2 == 0:
            row, _ = self.get_dimension(None)
            blank_row = self.rows - row  # count row from last
            if blank_row % 2 and inversions % 2 == 0:
                return True
            if blank_row % 2 == 0 and inversions % 2:
                return True
        return False


class Solver:

    # // find a solution to the initial board (using the A* algorithm)
    def __init__(self, obj):
        self.initial_board = obj
        self.current_board = self.initial_board
        self.to_be_seen = MinPQ()
        self.to_be_seen.insert(obj)
        self.already_seen = []
        self.moves = 0

    # // min number of moves to solve initial board; -1 if unsolvable
    def moves(self):
        return len(self.current_board.path)

    def add_tobe(self, board):
        for every_board in self.already_seen:
            if board.array == every_board.array:
                return 0
        self.to_be_seen.insert(board)

    def add_already(self, board):
        self.already_seen.append(board)

    def get_nxt(self):
        board = self.to_be_seen.remove()
        if board == -1:
            return -1
        for every_board in self.already_seen:
            if board.array == every_board.array:
                return None
        return board

    def get_next(self):
        bord = None
        while bord is None:
            bord = self.get_nxt()
        return bord

    def solution(self):
        if not self.current_board.isSolvable():
            return -1

        while True:
            self.current_board = self.get_next()
            if self.current_board == -1:
                break
            if self.current_board.is_goal():
                new_path = self.current_board.path[1:]
                new_path.append(self.current_board.last_direction)
                break

            # current_board.to_string()
            nebors = self.current_board.neighbours(lastdirection=self.current_board.last_direction)
            self.add_already(self.current_board)
            for ne in nebors:
                self.add_tobe(ne)
        return new_path


pygame.init()


def new_puzzle():
    given_rows = 3
    given_cols = 3
    plane = []
    n = len(plane)
    while n < 9:
        item = random.randrange(0, 9)
        if item == 0:
            item = None
        if item in plane:
            continue
        else:
            plane.append(item)
        n = len(plane)

    i = 0
    given_array = [[None for i in range(given_cols)] for j in range(given_rows)]
    for row in range(given_rows):
        for col in range(given_cols):
            given_array[row][col] = plane[i]
            i += 1

    puzzle = Board(3, 3, given_array)
    if not puzzle.isSolvable():
        puzzle = new_puzzle()

    return puzzle


pygame.init()

Display_Width = 500
Display_Height = 600

BASICFONT = pygame.font.Font('freesansbold.ttf', 80)
namasteFONT = pygame.font.SysFont('lucidahandwriting', 80)
gameDisplay = pygame.display.set_mode((Display_Width, Display_Height), 0, 32)
pygame.display.set_caption('PuzzLE')
clock = pygame.time.Clock()
BLACK = (0, 0, 0)
RED = (255, 50, 20)
GREEN = (0, 255, 0)
YELLOW = (250, 250, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)

hint = pygame.image.load('.img//hint.png')
solveMe = pygame.image.load('.img//giveup.png')
reset = pygame.image.load('.img//reset.png')
namaste = pygame.image.load('.img//Namaste.png')
hint_click = pygame.image.load('.img//hint_enlarged.png')
solveMe_click = pygame.image.load('.img//giveup_enlarged.png')
reset_click = pygame.image.load('.img//reset_enlarged.png')

hint_pos = (360, 10)
solveMe_pos = (100, -10)
reset_pos = (5, 0)
hint_Epos = (330, 0)
solveMe_Epos = (90, 0)
reset_Epos = (0, 0)
namaste_pos = (100, 30)
# |-|-|-|
button_up = 0
button_down = 150
reset_start = 0
solveMe_start = 180
hint_start = 320
button_end = 450
user_moves = 0


def swap(move):
    array = Puzzle.array
    x0 = 0
    y0 = 0
    for i in range(len(array)):
        for j in range(len(array[0])):
            if array[i][j] is None:
                x0, y0 = i, j

    x1 = x0
    y1 = y0
    if move == "left" and y0 > 0:
        y1 -= 1
        array[x0][y0], array[x1][y1] = array[x1][y1], array[x0][y0]
    elif move == "right" and y0 < len(array[0]) - 1:
        y1 += 1
        array[x0][y0], array[x1][y1] = array[x1][y1], array[x0][y0]
    elif move == "up" and x0 > 0:
        x1 -= 1
        array[x0][y0], array[x1][y1] = array[x1][y1], array[x0][y0]
    elif move == "down" and x0 < len(array) - 1:
        x1 += 1
        array[x0][y0], array[x1][y1] = array[x1][y1], array[x0][y0]


def take_action(cur, drawButton = True):
    x, y = cur[0], cur[1]
    button_action = None
    if button_down > y > button_up and button_end > x > reset_start:
        # button_area
        if x < solveMe_start:
            button_action = 'reset'
        elif x > hint_start:
            button_action = 'hint'
        else:
            button_action = 'solveMe'
    if drawButton:
        drawButtons(button_action)
    return button_action


def show_puzzle(goal=False):
    global Puzzle
    array = Puzzle.array
    blockTOP = 130
    blockLEFT = 20
    blockSIZE = 150
    initialLEFT = blockLEFT
    border_blocks = []
    blocks = []
    border_SIZE = 10
    if Puzzle.is_goal():
        block_COLOR = YELLOW
    else:
        block_COLOR = RED
    for i in range(len(array)):
        for j in range(len(array[0])):
            border_blocks.append({'rect': pygame.Rect(blockLEFT, blockTOP, blockSIZE, blockSIZE), 'color': WHITE})
            if array[i][j] is None:
                blocks.append(
                    {'rect': pygame.Rect(blockLEFT + border_SIZE, blockTOP + border_SIZE, blockSIZE - 2 * border_SIZE,
                                         blockSIZE - 2 * border_SIZE), 'color': BLACK, 'block': str('')})
            else:
                blocks.append({'rect': pygame.Rect(blockLEFT + border_SIZE, blockTOP + border_SIZE,
                                                   blockSIZE - 2 * border_SIZE, blockSIZE - 2 * border_SIZE),
                               'color': block_COLOR, 'block': str(array[i][j])})
            blockLEFT += blockSIZE
        blockTOP += blockSIZE
        blockLEFT = initialLEFT

    # border for puzzle blocks
    for b in border_blocks:
        pygame.draw.rect(gameDisplay, b['color'], b['rect'])
    # text and blocks
    for b in blocks:
        pygame.draw.rect(gameDisplay, b['color'], b['rect'])
        textSurf = BASICFONT.render(b['block'], True, (0, 0, 0))
        textRect = textSurf.get_rect()
        textRect.center = b['rect'].left + (blockSIZE / 2) - border_SIZE, b['rect'].top + (blockSIZE / 2) - border_SIZE
        gameDisplay.blit(textSurf, textRect)


def drawButtons(cursor=None):
    if cursor is None:
        gameDisplay.blit(hint, hint_pos)
        gameDisplay.blit(reset, reset_pos)
        gameDisplay.blit(solveMe, solveMe_pos)
    else:
        if cursor == 'hint':
            gameDisplay.blit(hint_click, hint_Epos)
            gameDisplay.blit(reset, reset_pos)
            gameDisplay.blit(solveMe, solveMe_pos)
        elif cursor == 'solveMe':
            gameDisplay.blit(hint, hint_pos)
            gameDisplay.blit(reset, reset_pos)
            gameDisplay.blit(solveMe_click, solveMe_Epos)
        elif cursor == 'reset':
            gameDisplay.blit(hint, hint_pos)
            gameDisplay.blit(reset_click, reset_Epos)
            gameDisplay.blit(solveMe, solveMe_pos)


def GUI():
    global Puzzle
    gameEXIT = False
    next_move = None
    gameDisplay.fill((125, 182, 243))
    # INput
    cur = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameEXIT = True
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                next_move = 'left'
            elif event.key == pygame.K_RIGHT:
                next_move = 'right'
            elif event.key == pygame.K_UP:
                next_move = 'up'
            elif event.key == pygame.K_DOWN:
                next_move = 'down'
        if event.type == pygame.MOUSEBUTTONDOWN:
            action = take_action(cur)
            if action == 'hint':
                if Puzzle.is_goal():
                    return 0
                # print("SHOW THE HINT ")
                hintSolver()
            elif action == 'reset':
                # print("shuffle the puzzle/ restart")
                gameStart()
                exit()
            elif action == 'solveMe':
                if Puzzle.is_goal():
                    return 0
                # print("SHOW THE FULL SOLUTION")
                fullSolver()
                #optional if you want to restart automatically
#                 time.sleep(5)
#                 gameStart()
#                 exit()
    # Actions
    if next_move is not None:
        swap(next_move)

    if Puzzle.isSolvable():
        show_puzzle(goal=True)
    else:
        show_puzzle()
    take_action(cur)
    pygame.display.update()
    clock.tick(30)
    return gameEXIT


def fullSolver():
    global Puzzle
    fullSolver = Solver(Puzzle)
    full_path = fullSolver.solution()
    for each_path in full_path:
        for event in pygame.event.get():
            cur = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                action = take_action(cur, drawButton=False)
                if action == 'reset':
                    # print("shuffle the puzzle/ restart")
                    gameStart()
                    exit()
        swap(each_path)
        show_puzzle()
        pygame.display.update()
        time.sleep(0.7)


def hintSolver():
    global Puzzle
    hintSolver = Solver(Puzzle)
    hint_path = hintSolver.solution()
    swap(hint_path[0])
    show_puzzle()
    pygame.display.update()
    time.sleep(0.1)

def game_intro():
    gameDisplay.fill(YELLOW)
    gameDisplay.blit(namaste, namaste_pos)
    textSurf = namasteFONT.render("NAMASTE", True, (0, 0, 0))
    textRect = textSurf.get_rect()
    textRect.center = namaste_pos[0] + 150, namaste_pos[1] + 450
    gameDisplay.blit(textSurf, textRect)
    pygame.display.update()
    time.sleep(1)

def gameStart():
    global Puzzle
    Puzzle = new_puzzle()
    while True:
        GUI()

game_intro()
gameStart()
