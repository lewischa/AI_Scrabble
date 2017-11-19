"""
Author: Chad Lewis
File:   scrabble.py
"""

from tile import ScrabbleTile
from scrabble_dfa import DFA

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
        self.staged_letters_by_coord = {}
        self.dfa = DFA()

    def set_letter(self, row, col, letter):
        self.player_board[row][col] = letter
        self.staged_letters_by_coord[row, col] = letter
        print(self.staged_letters_by_coord)
        self.play_hand()

    def is_vertically_aligned(self, coords):
        """Check vertical alignment

        Tiles are considered vertically aligned if each tile's column is the
        same, and there is no gap (i.e. letterless-square) between the first
        and last tiles placed.
        NOTE: placed tiles do not have to be adjacent -- they can be placed
              around existing tiles that were played previously
        """
        if all(coord[1] == coords[0][1] for coord in coords):
            #   Letters are vertically aligned, but may not be adjacent
            current = coords[0]
            coord_below = (current[0] + 1, current[1])
            #   Ensure we stay on the board
            while coord_below[0] <= 14:
                row, col = current
                if not self.player_board[row][col]:
                    #   If there's no letter at the current coordinate,
                    #   current's row should have passed the row of the
                    #   last tile placed by the player.
                    #   i.e. current[0] > coords[-1][0]
                    return current[0] > coords[-1][0]
                current = coord_below
                coord_below = (current[0] + 1, current[1])
            return True
        return False

    def is_horizontally_aligned(self, coords):
        """Check horizontal alignment

        Tiles are considered horizontally aligned if each tile's row is the
        same, and there is no gap (i.e. letterless-square) between the first
        and last tiles placed.
        NOTE: as with vertical alignment, tiles do not need to be adjacent --
              they can be placed around existing tiles that were played
              previously
        """
        if all(coord[0] == coords[0][0] for coord in coords):
            #   Letters are horizontally aligned, but may not be adjacent
            current = coords[0]
            coord_right = (current[0], current[1] + 1)
            #   Ensure we stay on the board
            while coord_right[1] <= 14:
                row, col = current
                if not self.player_board[row][col]:
                    #   If there's no letter at the current coordinate,
                    #   current's column should have passed the column of
                    #   the last tile placed by the player.
                    #   i.e. current[1] > coords[-1][1]
                    return current[1] > coords[-1][1]
                current = coord_right
                coord_right = (current[0], current[1] + 1)
            return True
        return False

    def is_legal_vertical_word(self, coords, check_horizontal):
        """Check if the vertically-played word is acceptable

        A word is acceptable if it is in the Scrabble dictionary,
        determined by self.dfa

        Args:
            -- coords: List of coordinates where user has placed tiles
            -- check_horizontal: True/False; whether or not to check
                                 for legal words horizontally from
                                 current position
        """

        vertical_word = []
        #   current represents the tile played by the user that is
        #   closest to the top of the board
        current = coords[0]
        #   coord_above is the coordinate immediately above current
        coord_above = (current[0] - 1, current[1])

        #   Ensure that the coordinate we're looking at stays on
        #   the board
        while coord_above[0] >= 0:
            #   This loop moves up the board to find the topmost square
            #   that contains a letter above what the user has played.
            #   This is necessary since words can be extended off
            #   words played previously.
            row, col = coord_above
            if not self.player_board[row][col]:
                #   This ensures there is a letter in the position of
                #   coord_above. If not, break out.
                break
            current = coord_above
            coord_above = (current[0] - 1, current[1])

        #   coord_below is the coordinate immediately below current
        coord_below = (current[0] + 1, current[1])

        #   Again, ensure that the coordinate we're looking at stays
        #   on the board
        while coord_below[0] <= 14:
            row, col = current
            vertical_word.append(self.player_board[row][col])
            if not self.player_board[coord_below[0]][coord_below[1]]:
                #   This ensures there is a letter in the position of
                #   coord_below. If not, break out.
                break
            if check_horizontal and current in coords:
                #   If the user placed a tile at the current coordinate,
                #   we should perform a horizontal cross-check.
                #   This is not necessary if the tile at the current
                #   coordinate was played in a previous turn (the previous
                #   turn already validated any words off that tile)
                if self.is_legal_horizontal_word([current], False):
                    print("Horizontal cross-check passed")
            current = coord_below
            coord_below = (current[0] + 1, current[1])

        print("Legal vertical word: {}".format(''.join(vertical_word)))
        return self.dfa.accepts(''.join(vertical_word))

    def is_legal_horizontal_word(self, coords, check_vertical):
        """Check if the horizontally-played word is acceptable

        A word is acceptable if it is in the Scrabble dictionary,
        determined by self.dfa

        Args:
            -- coords: List of coordinates where user has placed tiles
            -- check_vertical: True/False; whether or not to check
                               for legal words vertically from
                               current position
        """

        horizontal_word = []

        #   current represents the tile played by the user that is
        #   closest to the left side of the board
        current = coords[0]
        #   coord_left is the coordinate immediately left of current
        coord_left = (current[0], current[1] - 1)

        #   Ensure the coordinate we're looking at stays on the board
        while coord_left[1] >= 0:
            #   This loop moves left on the board to find the furthest square
            #   that contains a letter left of what the user has played.
            #   This is necessary since words can be extended off
            #   words played previously.
            row, col = coord_left
            if not self.player_board[row][col]:
                #   This ensures there is a letter in the position of
                #   coord_left. If not, break out.
                break
            current = coord_left
            coord_left = (current[0], current[1] - 1)

        #   coord_right is the coordinate immediately right of current
        coord_right = (current[0], current[1] + 1)

        #   Stay on the board
        while coord_right[1] <= 14:
            row, col = current
            horizontal_word.append(self.player_board[row][col])
            if not self.player_board[coord_right[0]][coord_right[1]]:
                #   This ensures there is a letter in the position of
                #   coord_right. If not, break out.
                break
            if check_vertical and current in coords:
                #   If the user placed a tile at the current coordinate,
                #   we should perform a vertical cross-check.
                #   This is not necessary if the tile at the current
                #   coordinate was played in a previous turn (the previous
                #   turn already validated any words off that tile)
                if self.is_legal_vertical_word([current], False):
                    print("Vertical cross-check passed")
            current = coord_right
            coord_right = (current[0], current[1] + 1)

        print("Legal horizontal word: {}".format(''.join(horizontal_word)))
        return self.dfa.accepts(''.join(horizontal_word))

    def play_hand(self):
        #   self.staged_letters_by_coord has keys in the form (row, col)
        #   pull them out --> coords: [(row, col), (row, col), ...]
        coords = [coord for coord in self.staged_letters_by_coord]
        #   Sorting the coordinates makes it easier to loop through them
        #   in order, so the first coordinate would be the first letter
        #   of the consecutive letters placed by the user
        coords.sort()
        print("in play_hand, coords: {}\n".format(coords))
        if self.is_vertically_aligned(coords):
            print("I'm vert aligned")
            if self.is_legal_vertical_word(coords, True):
                print("Vertical word is legal")
        elif self.is_horizontally_aligned(coords):
            print "I'm horiz aligned"
            if self.is_legal_horizontal_word(coords, True):
                print("Horizontal word is legal")


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
