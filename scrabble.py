"""
Author: Chad Lewis
File:   scrabble.py
"""

from tile import ScrabbleTile
from scrabble_dfa import DFA

#   Some useful 'constants'
LITERAL_MAX_LENGTH = 15
MAX_LENGTH = 14
CENTER = (7,7)

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
        self._is_premium_letter = (square_type == 'double_letter'
                                  or square_type == 'triple_letter')
        self._is_premium_word = (square_type == 'double_word'
                                or square_type == 'triple_word')
        self.available = True
        self.played = False

    def is_premium_letter(self):
        return self._is_premium_letter

    def is_premium_word(self):
        return self._is_premium_word

    def get_multiplier(self):
        return self.multiplier_by_square_type[self.square_type]

    def is_available(self):
        if not self.is_played():
            return self.available
        return False

    def set_is_played(self):
        """This renders the tile unusable for the rest of the game."""
        self.played = True

    def is_played(self):
        return self.played

    def set_availability(self, availability):
        if not self.is_played():
            self.available = availability

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
        self.player_board = [
            [
                '' for _ in range(LITERAL_MAX_LENGTH)
            ] for _ in range(LITERAL_MAX_LENGTH)
        ]
        self.staged_letters_by_coord = {}

        #   `anchor_coords` will keep track of coordinates immediately
        #   adjacent to current tiles on the board. Initialize this to contain
        #   the board's center coordinate, because the very first hand MUST
        #   be played using this coordinate.
        self.anchor_coords = set([CENTER])
        self.dfa = DFA()

    def set_letter(self, row, col, letter):
        # self.player_board[row][col] = letter
        # self.staged_letters_by_coord[row, col] = letter
        # print(self.staged_letters_by_coord)
        # score = self.get_hand_legality_by_score()
        # if score:
        #     print("\nLegal hand score: {}".format(score))
        # else:
        #     print("\nIllegal move.")
        print("set_letter stub")

    def get_letter_score(self, row, col, letters_by_coord):
        """Get the score of the letter placed at (row, col).

        This will also take into account whether or not the letter is placed on
        top of a double-letter or triple-letter ScrabbleSquare, in which case
        the multiplier will only be awarded if (row, col) is in
        self.staged_letters_by_coord (i.e. the location we're looking at is a
        tile placed by the player in the CURRENT turn. Previous turns that
        used a multiplier square "consume" the multiplier).
        """

        letter = self.get_letter_at_coord(row, col, letters_by_coord)
        base_value = ScrabbleTile(letter=letter).get_value()
        multiplier = 1
        if (row, col) in letters_by_coord:
            if self.base_board[row][col].is_premium_letter():
                multiplier *= self.base_board[row][col].get_multiplier()
        return base_value * multiplier

    def get_word_multiplier(self, row, col, letters_by_coord):
        """Get the word multiplier at (row, col) if there is one.

        This method returns a multiplier other than 1 if, and only if,
        (row, col) is in self.staged_letters_by_coord (it's a location the
        player has actually placed a tile) and there is actually a word
        multiplier square at (row, col).
        """

        if (row, col) in letters_by_coord:
            if self.base_board[row][col].is_premium_word():
                multiplier = self.base_board[row][col].get_multiplier()
                return multiplier
        return 1

    def get_letter_at_coord(self, row, col, letters_by_coord):
        """This method gets the letter at `row`, `col`.

        Since letters will not be immediately stored in `self.player_board`,
        this method checks both `self.player_board` and `letters_by_coord` if
        a letter exists at the given coordinate. Returns '' if no letter is
        present.
        """

        if self.player_board[row][col]:
            return self.player_board[row][col]
        else:
            if (row, col) in letters_by_coord:
                return letters_by_coord[row, col]
        return ''

    def is_vertically_aligned(self, coords, letters_by_coord):
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
            while coord_below[0] <= MAX_LENGTH:
                row, col = current
                if not self.get_letter_at_coord(row, col, letters_by_coord):
                    #   If there's no letter at the current coordinate,
                    #   current's row should have passed the row of the
                    #   last tile placed by the player.
                    #   i.e. current[0] > coords[-1][0]
                    return current[0] > coords[-1][0]
                current = coord_below
                coord_below = (current[0] + 1, current[1])
            return True
        return False

    def is_horizontally_aligned(self, coords, letters_by_coord):
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
            while coord_right[1] <= MAX_LENGTH:
                row, col = current
                if not self.get_letter_at_coord(row, col, letters_by_coord):
                    #   If there's no letter at the current coordinate,
                    #   current's column should have passed the column of
                    #   the last tile placed by the player.
                    #   i.e. current[1] > coords[-1][1]
                    return current[1] > coords[-1][1]
                current = coord_right
                coord_right = (current[0], current[1] + 1)
            return True
        return False

    def is_legal_vertical_word(self, coords,
                               letters_by_coord, check_horizontal):
        """Check if the vertically-played word is acceptable

        A word is acceptable if it is in the Scrabble dictionary,
        determined by self.dfa.

        This method returns the score of the word if it's accepted, and 0
        if not accepted.

        Args:
            -- coords: List of coordinates where user has placed tiles
            -- check_horizontal: True/False; whether or not to check
                                 for legal words horizontally from
                                 current position
        """

        #   Keep a running score of the word being checked
        word_score = 0
        #   Keep a running score of the cross-checks
        cross_check_score = 0
        #   Keep track of whether a tile is played on a double-word or
        #   triple-word ScrabbleSquare
        word_multiplier = 1

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
            if not self.get_letter_at_coord(row, col, letters_by_coord):
                #   This ensures there is a letter in the position of
                #   coord_above. If not, break out.
                break
            current = coord_above
            coord_above = (current[0] - 1, current[1])

        #   coord_below is the coordinate immediately below current
        coord_below = (current[0] + 1, current[1])

        #   Again, ensure that the coordinate we're looking at stays
        #   on the board
        while coord_below[0] <= LITERAL_MAX_LENGTH:
            row, col = current
            vertical_word.append(
                self.get_letter_at_coord(row, col, letters_by_coord))
            word_score += self.get_letter_score(row, col, letters_by_coord)
            word_multiplier *= self.get_word_multiplier(row,
                                                        col,
                                                        letters_by_coord)
            # try:
                # if not self.get_letter_at_coord(coord_below[0],
                #                                 coord_below[1],
                #                                 letters_by_coord):
                # if not self.player_board[coord_below[0]][coord_below[1]]:
                    #   This ensures there is a letter in the position of
                    #   coord_below. If not, break out.
                    # break
            # except IndexError:
            #     break
            if check_horizontal and current in coords:
                #   If the user placed a tile at the current coordinate,
                #   we should perform a horizontal cross-check.
                #   This is not necessary if the tile at the current
                #   coordinate was played in a previous turn (the previous
                #   turn already validated any words off that tile)
                new_cross_check_score = self.is_legal_horizontal_word(
                                            [current], letters_by_coord, False)
                if new_cross_check_score is None:
                    #   is_legal_horizontal_word() returns None if the
                    #   horizontal word being checked is not legal. If that
                    #   word is not legal, the entire hand cannot be played,
                    #   so return None.
                    return None
                else:
                    #   The cross-check was completed successfully and the
                    #   horizontal word in the cross-check is legal. Keep
                    #   track of that word's score.
                    cross_check_score += new_cross_check_score

            if not self.get_letter_at_coord(coord_below[0],
                                            coord_below[1],
                                            letters_by_coord):
                break
            current = coord_below
            coord_below = (current[0] + 1, current[1])

        #   Cross-checks are always performed the first time this method is
        #   called. This causes a problem if there's no word formed
        #   perpendicular to the coordinate we're currently checking, because
        #   a cross-check could be called on a single letter, say 't', which
        #   is not a valid Scrabble word. This if/elif block catches this issue
        #   by only checking that `vertical_word` is acceptable if its
        #   length is more than 1. This also prevents single-letter words
        #   at the beginning of the game, which is an added bonus.
        if len(vertical_word) > 1:
            if self.dfa.accepts(''.join(vertical_word)):
                #   The word is accepted. Multiply its score by the
                #   `word_multiplier` we've accumulated, and add the
                #   `cross_check_score` to that product to get the final
                #   score of the legal word plus perpendicular words formed
                #   from it.
                return word_score * word_multiplier + cross_check_score
            else:
                #   One or all of the words is illegal, so return None.
                return None
        elif not check_horizontal:
            #   `check_horizontal` is False, so that means we're currently
            #   performing a cross-check. As stated above, single-letter
            #   cross-check words should not add value to the hand. Return 0.
            return 0

    def is_legal_horizontal_word(self, coords,
                                 letters_by_coord, check_vertical):
        """Check if the horizontally-played word is acceptable

        A word is acceptable if it is in the Scrabble dictionary,
        determined by self.dfa.

        This method returns the score of the word if it's accepted, and 0
        if not accepted.

        Args:
            -- coords: List of coordinates where user has placed tiles
            -- check_vertical: True/False; whether or not to check
                               for legal words vertically from
                               current position
        """

        #   Keep a running score of the word being checked
        word_score = 0
        #   Keep a running score of the cross-checks
        cross_check_score = 0
        #   Keep track of whether a tile is played on a double-word or
        #   triple-word ScrabbleSquare
        word_multiplier = 1

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
            if not self.get_letter_at_coord(row, col, letters_by_coord):
                #   This ensures there is a letter in the position of
                #   coord_left. If not, break out.
                break
            current = coord_left
            coord_left = (current[0], current[1] - 1)

        #   coord_right is the coordinate immediately right of current
        coord_right = (current[0], current[1] + 1)

        #   Stay on the board
        while coord_right[1] <= LITERAL_MAX_LENGTH:
            row, col = current
            horizontal_word.append(
                self.get_letter_at_coord(row, col, letters_by_coord))
            word_score += self.get_letter_score(row, col, letters_by_coord)
            word_multiplier *= self.get_word_multiplier(row,
                                                        col,
                                                        letters_by_coord)
            # try:
                # if not self.get_letter_at_coord(coord_right[0],
                #                                 coord_right[1],
                #                                 letters_by_coord):
                # if not self.player_board[coord_right[0]][coord_right[1]]:
                    #   This ensures there is a letter in the position of
                    #   coord_right. If not, break out.
            #         break
            # except IndexError:
            #     break
            if check_vertical and current in coords:
                #   If the user placed a tile at the current coordinate,
                #   we should perform a vertical cross-check.
                #   This is not necessary if the tile at the current
                #   coordinate was played in a previous turn (the previous
                #   turn already validated any words off that tile)
                new_cross_check_score = self.is_legal_vertical_word(
                                            [current], letters_by_coord, False)
                if new_cross_check_score is None:
                    #   is_legal_vertical_word() returns None if the
                    #   vertical word being checked is not legal. If that
                    #   word is not legal, the entire hand cannot be played,
                    #   so return None.
                    return None
                else:
                    #   The cross-check was completed successfully and the
                    #   vertical word in the cross-check is legal. Keep
                    #   track of that word's score.
                    cross_check_score += new_cross_check_score

            if not self.get_letter_at_coord(coord_right[0],
                                            coord_right[1],
                                            letters_by_coord):
                break
            current = coord_right
            coord_right = (current[0], current[1] + 1)

        #   Cross-checks are always performed the first time this method is
        #   called. This causes a problem if there's no word formed
        #   perpendicular to the coordinate we're currently checking, because
        #   a cross-check could be called on a single letter, say 't', which
        #   is not a valid Scrabble word. This if/elif block catches this issue
        #   by only checking that `horizontal_word` is acceptable if its
        #   length is more than 1. This also prevents single-letter words
        #   at the beginning of the game, which is an added bonus.
        if len(horizontal_word) > 1:
            if self.dfa.accepts(''.join(horizontal_word)):
                #   The word is accepted. Multiply its score by the
                #   `word_multiplier` we've accumulated, and add the
                #   `cross_check_score` to that product to get the final
                #   score of the legal word plus perpendicular words formed
                #   from it.
                return word_score * word_multiplier + cross_check_score
            else:
                #   One or all of the words is illegal, so return None.
                return None
        elif not check_vertical:
            #   `check_vertical` is False, so that means we're currently
            #   performing a cross-check. As stated above, single-letter
            #   cross-check words should not add value to the hand. Return 0.
            return 0


    def get_hand_legality_by_score(self, letters_by_coord):
        """Returns the score of a legal hand.

        This method will both check the legality of a word and return its score
        if it's legal. If the word is illegal, this method returns 0.
        """

        #   letters_by_coord has keys in the form (row, col)
        #   pull them out --> coords: [(row, col), (row, col), ...]
        coords = [coord for coord in letters_by_coord]

        #   This check verifies that at least one of the tiles staged for
        #   a possible hand is in `self.anchor_coords`. The rules of Scrabble
        #   require that every word must be immediately adjacent to at least
        #   1 tile that already exists on the board.
        #
        #   The first time this method is called after the game starts,
        #   this verifies that at least one of the tiles staged has been
        #   placed on the center square.
        if not any(coord in self.anchor_coords for coord in coords):
            return 0
        #   Sorting the coordinates makes it easier to loop through them
        #   in order, so the first coordinate would be the first letter
        #   of the consecutive letters placed by the user
        coords.sort()
        if self.is_vertically_aligned(coords, letters_by_coord):
            vertical_word_score = self.is_legal_vertical_word(coords,
                                                              letters_by_coord,
                                                              True)
            if vertical_word_score:
                return vertical_word_score
        elif self.is_horizontally_aligned(coords, letters_by_coord):
            horizontal_word_score = self.is_legal_horizontal_word(
                                        coords, letters_by_coord, True)
            if horizontal_word_score:
                return horizontal_word_score
        #   Word is not legal. Return 0.
        return 0

    def play_hand(self, letters_by_coord):
        score = self.get_hand_legality_by_score(letters_by_coord)
        if score:
            for (row, col), letter in letters_by_coord.iteritems():
                self.player_board[row][col] = letter
                self.permanently_place_tile(row, col)
            coords = [coord for coord in letters_by_coord]
            self.update_anchor_coords(coords)

        return score

    def update_anchor_coords(self, coords):
        """Help keep track of 'anchor' coordinates.

        'Anchor' coordinates are those immediately adjacent to (e.g. touching)
        coordinates with existing tiles. This helps facilitate the AI player's
        ability to choose 'good' locations to try to place a word.
        """

        def get_adjacent_coords(coord):
            """Get the coordinates adjacent to `coord`.

            This will return a list of coordinates encircling `coord`,
            less the coordinates that are in `coords`, have existing tiles,
            or are not on the board.
            """

            adjacent = []

            #   Only pick up the adjacent coordinates that are within bounds
            #   of the board
            if coord[0] != 0:
                adjacent.append((coord[0] - 1, coord[1]))
            if coord[0] != MAX_LENGTH:
                adjacent.append((coord[0] + 1, coord[1]))
            if coord[1] != 0:
                adjacent.append((coord[0], coord[1] - 1))
            if coord[1] != MAX_LENGTH:
                adjacent.append((coord[0], coord[1] + 1))

            #   Filter out the coordinates that are in `coords` or are
            #   not available (there is already a tile there).
            adjacent = filter(
                lambda c:
                    c not in coords
                    and self.base_board[c[0]][c[1]].is_available(),
                    adjacent)
            return adjacent

        adjacent_coords = []
        #   Build up the adjacent coordinates
        for coord in coords:
            adjacent_coords += get_adjacent_coords(coord)

        #   Update the `anchor_coords` set with the adjacent coordinates
        #   we've built up
        self.anchor_coords.update(adjacent_coords)

        #   Remove each coordinate in `coords` from the `anchor_coords` set
        #   if it exists (placing a tile at a coordinate renders that location
        #   unusable, and thus cannot be an anchor anymore).
        #
        #   Unfortunately Python does not allow passing a list to set.discard(),
        #   so we have to iterate.
        for coord in coords:
            self.anchor_coords.discard(coord)

    def is_available(self, row, col):
        if row > MAX_LENGTH or col > MAX_LENGTH:
            return False
        return self.base_board[row][col].is_available()

    def is_played(self, row, col):
        if row > MAX_LENGTH or col > MAX_LENGTH:
            return False
        return self.base_board[row][col].is_played()

    def set_availability(self, row, col, availability):
        if row <= MAX_LENGTH and col <= MAX_LENGTH:
            self.base_board[row][col].set_availability(availability)

    def permanently_place_tile(self, row, col):
        """Permanently set tile's availability to False

        This function will typically be called when a 'turn' is
        finalized. In other words, once a tile is placed and the 'turn'
        is done, no other tiles can be placed in that position for the
        duration of the game.
        """
        if row <= MAX_LENGTH and col <= MAX_LENGTH:
            self.base_board[row][col].set_is_played()
