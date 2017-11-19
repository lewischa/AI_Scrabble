"""
Author: Chad Lewis
File:   scrabble.py
"""

from tile import ScrabbleTile

class ScrabbleSquare(object):
    """This class represents one square on a Scrabble game board"""

    multiplier_by_square_type = {
        None: 1,
        'center': 1,
        'double_letter': 2,
        'triple_letter': 3,
        'double_word': 2,
        'triple_word': 3
    }

    def __init__(self, square_type=None):
        """
        Keyword Arguments:
        square_type -- Defines whether the square has a point multiplier
            Acceptable Values:
                - 'double_letter'
                - 'triple_letter'
                - 'double_word'
                - 'triple_word'
                - 'center'
                - None (regular square)
        """
        self.square_type = square_type
        self.is_premium_letter = (square_type == 'double_letter'
                                  or square_type == 'triple_letter')
        self.is_premium_word = (square_type == 'double_word'
                                or square_type == 'triple_word')
        self.available = True
        self.permanently_available = True

    def is_premium_letter(self):
        return self.is_premium_word

    def is_premium_word(self):
        return self.is_premium_letter

    def get_multiplier(self):
        return self.multiplier_by_square_type[self.square_type]

    def is_available(self):
        if self.permanently_available:
            return self.available
        return False

    def set_availability(self, availability):
        if self.permanently_available:
            self.available = availability

    def set_permanent_availability(self, availability):
        self.permanently_available = availability

    def shorthand(self):
        if self.square_type is None:
            return '  '
        elif self.square_type == 'center':
            return 'cs'
        else:
            return self.square_type[0] + self.square_type[7]

class ScrabbleBoard(object):
    """A representation of a Scrabble game board
    """

    #   This represents the upper left quadrant of the scrabble board,
    #       including the middle line but excluding the bottom line.
    #
    #   '' - regular square
    #   cs - center square
    #   dl - double letter
    #   tl - triple letter
    #   dw - double word
    #   tw - triple word
    top_left_quadrant = [
        ['tw','','','dl','','','','tw'],
        ['','dw','','','','tl','',''],
        ['','','dw','','','','dl',''],
        ['dl','','','dw','','','','dl'],
        ['','','','','dw','','',''],
        ['','tl','','','','tl','',''],
        ['','','dl','','','','dl','']
    ]

    #   This represents the middle row from the left side of the board up to
    #       and including the square in the very center of the board.
    middle_row = ['tw','','','dl','','','','cs']

    square_type_hash = {
        '': None,
        'cs': 'center',
        'dl': 'double_letter',
        'tl': 'triple_letter',
        'dw': 'double_word',
        'tw': 'triple_word'
    }

    def build_board(self):
        board = []
        #   This section builds the top half (excluding middle row)
        for type_row in self.top_left_quadrant:
            row = []
            for stype in type_row:
                row.append(ScrabbleSquare(
                    square_type=self.square_type_hash[stype]))
            for stype in type_row[-2::-1]:
                row.append(ScrabbleSquare(
                    square_type=self.square_type_hash[stype]))
            board.append(row)

        #   This section builds the middle row
        mid_row = []
        for stype in self.middle_row:
            mid_row.append(ScrabbleSquare(
                square_type=self.square_type_hash[stype]))
        for stype in self.middle_row[-2::-1]:
            mid_row.append(ScrabbleSquare(
                square_type=self.square_type_hash[stype]))
        board.append(mid_row)

        #   This section builds the bottom half (excluding mid. row)
        for type_row in self.top_left_quadrant[::-1]:
            row = []
            for stype in type_row:
                row.append(ScrabbleSquare(
                    square_type=self.square_type_hash[stype]))
            for stype in type_row[-2::-1]:
                row.append(ScrabbleSquare(
                    square_type=self.square_type_hash[stype]))
            board.append(row)
        return board

    def __init__(self):
        self.base_board = self.build_board()
        self.player_board = [['' for _ in range(15)] for _ in range(15)]

    def set_letter(self, row, col, letter):
        self.player_board[row][col] = letter

    def is_available(self, row, col):
        if row > 14 or col > 14:
            return False
        return self.base_board[row][col].is_available()

    def set_availability(self, row, col, availability):
        if row <= 14 and col <= 14:
            self.base_board[row][col].set_availability(availability)

    def permanently_place_tile(self, row, col):
        """Permanently set tile's availability to False

        This function will typically be called when a 'turn' is
        finalized. In other words, once a tile is placed and the 'turn'
        is done, no other tiles can be placed in that position for the
        duration of the game.
        """
        if row <= 14 and col <= 14:
            self.base_board[row][col].set_permanent_availability(False)

    def print_board(self):
        print "*----" * 15 + '*'
        for row in self.board:
            squares_string = '|'
            for tile in row:
                squares_string += ' ' + tile.shorthand() + ' '
                squares_string += '|'
            print squares_string
            print "*----" * 15 + '*'

#------------------------------------------------------------------------------
