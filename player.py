class Player(object):
    """The base class of a Scrabble player.

    The human player will use this class because it has all the implementation
    it needs, but the AI can inherit from this class and override any methods
    it needs to. Specifically, it should probably override play_hand() by
    doing something similar to the following:

        def play_hand(self):
            #   Do whatever the AI needs to do to build a letters_by_coord
            #   dictionary, where (row, col) are keys and LOWERCASE letters
            #   are values: {(7,7): 'a', (7,8): 't'}
            #       This would correspond to the word 'at', that will be
            #       played on coordinates (7,7) and (7,8).
            #
            #   Then pass the letters_by_coord dictionary to super:
            super(<AI class name>, self).play_hand(
                {'letters_by_coord': letters_by_coord})

    Calling super like this will handle all the already-implemented logic
    to actually place the tiles on the board. It passes a dictionary
    {'letters_by_coord': letters_by_coord} because the super method uses
    **kwargs for keyword arguments, and expects 'letters_by_coord' to exist.
    """

    def __init__(self, board, tile_bag):
        self.scrabble_board = board
        self.tile_bag = tile_bag
        self.tiles = []
        self.score = 0
        self.draw_tiles(7)

    def get_score(self):
        """Return the player's score."""

        return self.score

    def draw_tiles(self, amount):
        """Draw `amount` tiles from the tile bag."""

        self.tiles += self.tile_bag.draw_tiles(amount)

    def increment_score(self, score):
        """Increase the score."""

        self.score += score

    def release_and_draw_tiles(self, letters):
        """Remove used tiles and draw from the tile bag."""

        #   Remove the tiles corresponding to the letters used in a hand
        for letter in letters:
            for tile in self.tiles:
                if letter == tile.get_letter():
                    self.tiles.remove(tile)
                    break

        #   Draw the number of tiles used in the hand
        self.draw_tiles(len(letters))

    def play_hand(self, **kwargs):
        letters_by_coord = kwargs['letters_by_coord']
        score = self.scrabble_board.play_hand(letters_by_coord)
        if score:
            self.increment_score(score)
            self.release_and_draw_tiles([l for l in letters_by_coord.values()])

        #   Return the score and the player's current letters
        return score, [tile.get_letter() for tile in self.tiles]

    def get_letters(self):
        """Return a list of letters that the player holds."""
        
        return [tile.get_letter() for tile in self.tiles]
