import math
import random
import sys

CONNECT = 3
COLS = 4
ROWS = 3
EMPTY = ' '
TIE = 'TIE'

class Connect3Board:

    def __init__(self, string=None):
        if string is not None:
            self.b = [list(line) for line in string.split('|')]
        else:
            self.b = [list(EMPTY * ROWS) for i in range(COLS)]

    def compact_string(self):
        return '|'.join([''.join(row) for row in self.b])

    def clone(self):
        return Connect3Board(self.compact_string())

    def get(self, i, j):
        return self.b[i][j] if i >= 0 and i < COLS and j >= 0 and j < ROWS else None

    def row(self, j):
        return [self.get(i, j) for i in range(COLS)]

    def put(self, i, j, val):
        self.b[i][j] = val
        return self

    def empties(self):
        return self.compact_string().count(EMPTY)

    def first_empty(self, i):
        j = ROWS - 1
        if self.get(i, j) != EMPTY:
            return None
        while j >= 0 and self.get(i, j) == EMPTY:
            j -= 1
        return j + 1

    def place(self, i, label):
        j = self.first_empty(i)
        if j is not None:
            self.put(i, j, label)
        return self

    def equals(self, board):
        return self.compact_string() == board.compact_string()

    def next(self, label):
        boards = []
        for i in range(COLS):
            j = self.first_empty(i)
            if j is not None:
                board = self.clone()
                board.put(i, j, label)
                boards.append(board)
        return boards

    def _winner_test(self, label, i, j, di, dj):
        for _ in range(CONNECT-1):
            i += di
            j += dj
            if self.get(i, j) != label:
                return False
        return True

    def winner(self):
        for i in range(COLS):
            for j in range(ROWS):
                label = self.get(i, j)
                if label != EMPTY:
                    if self._winner_test(label, i, j, +1, 0) \
                            or self._winner_test(label, i, j, 0, +1) \
                            or self._winner_test(label, i, j, +1, +1) \
                            or self._winner_test(label, i, j, -1, +1):
                        return label
        return TIE if self.empties() == 0 else None

    def __str__(self):
        return stringify_boards([self])
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ Player Class ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~  ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
class Player:
    def __init__(self, label=None):
        if label is not None:
            self.label = label
        else:
            self.label = 'X'

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ Random Player Class ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
class RandomPlayer(Player):
    def __init__(self, label=None):
        super().__init__(label)

    def makeMove(self, currentBoard, label):
        boardStates = currentBoard.next(label)
        return boardStates[random.randint(0, len(boardStates) - 1)]

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ Minimax Player Class ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~  ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
class MinimaxPlayer(Player):
    def __init__(self, label=None):
        super().__init__(label)
        if self.label == 'O':
            self.otherLabel = 'X'
        else:
            self.otherLabel = 'O'

    def makeMove(self, boardState, label):
        u = []
        nextBoards = boardState.next(label)
        for i in nextBoards:
            u.append(self.minValue(i))
        return nextBoards[u.index(max(u))]

    def maxValue(self, board):
        u = []
        if board.winner() is not None:
            return self.utility(board)
        v = -9999
        for n in board.next(self.label):
            u.append(max(v, self.minValue(n)))
        return max(u) * .9

    def minValue(self, board):
        u = []
        if board.winner() is not None:
            return self.utility(board)
        v = 9999
        for n in board.next(self.otherLabel):
            u.append(min(v, self.maxValue(n)))
        return min(u) * .9

    def utility(self, board):
        if board.winner() == self.label:
            return 1
        elif board.winner() == 'TIE':
            return 0
        else:
            return -1

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ Game Class ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~  ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
class Game:
    def __init__(self, startingBoard=None, p2Type=None):
        if startingBoard is not None:
            self.b = startingBoard
        else:
            self.b = Connect3Board()

        if p2Type is None:
            self.p2 = RandomPlayer('O')
        elif p2Type == 'm':
            self.p2 = MinimaxPlayer('O')
        else:
            print('Invalid Player 2 Type')

    def playGame(self):
        currentBoard = self.b
        path = [currentBoard]
        turn = 1
        while True:
            if currentBoard.winner() is None:
                pass
            else:
                return path
            print(currentBoard)
            if turn == 1:
                currentBoard = self.humanMove(currentBoard, 'X')
                path.append(currentBoard)
                turn = 2
            else:
                currentBoard = self.p2.makeMove(currentBoard, 'O')
                path.append(currentBoard)
                turn = 1

    def humanMove(self, board, label):
        while True:
            try:
                move = int(input("Enter Move (1 - 4):\n")) - 1
                break
            except:
                print("Error: Invalid input.")
        return board.place(move, label)

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ Methods ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
def stringify_boards(boards):
    if len(boards) > 6:
        return stringify_boards(boards[0:6]) + '\n' + stringify_boards(boards[6:])
    else:
        s = ' '.join([' ' + ('-' * COLS) +' '] * len(boards)) + '\n'
        for j in range(ROWS):
            rows = []
            for board in boards:
                rows.append('|' + ''.join(board.row(ROWS-1-j)) + '|')
            s += ' '.join(rows) + '\n'
        s += ' '.join([' ' + ('-' * COLS) +' '] * len(boards))
        return s

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ Main Method ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        board = Connect3Board(sys.argv[2] if len(sys.argv) > 2 else None)
        if cmd == 'print':
            print(board)
        elif cmd == 'next':
            print(stringify_boards(board.next('X')))
        elif cmd == 'random':
            game = Game(board)
            path = game.playGame()
            print(stringify_boards(path))
        elif cmd == 'minimax':
            game = Game(board, p2Type = 'm')
            path = game.playGame()
            print(stringify_boards(path))
