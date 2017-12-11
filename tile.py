"""
Author: Chad Lewis
File:   tile.py
"""

import random

value_by_letter = {
    'a':1,
    'b':3,
    'c':3,
    'd':2,
    'e':1,
    'f':4,
    'g':2,
    'h':4,
    'i':1,
    'j':8,
    'k':5,
    'l':1,
    'm':3,
    'n':1,
    'o':1,
    'p':3,
    'q':10,
    'r':1,
    's':1,
    't':1,
    'u':1,
    'v':4,
    'w':4,
    'x':8,
    'y':4,
    'z':10,
    ' ':0
}

num_tiles_by_letter = {
    'a':10,
    'b':2,
    'c':2,
    'd':4,
    'e':13,
    'f':2,
    'g':3,
    'h':2,
    'i':9,
    'j':1,
    'k':1,
    'l':4,
    'm':2,
    'n':6,
    'o':8,
    'p':2,
    'q':1,
    'r':6,
    's':4,
    't':6,
    'u':4,
    'v':2,
    'w':2,
    'x':1,
    'y':2,
    'z':1,
    ' ':0   # Blank tiles will not be used.
}

class ExchangeTileError(ValueError):
    """Exception that may be raised when exchanging tiles

    Raise this exception when the number of tiles to exchange
    exceeds the number of tiles left in the TileBag.
    """
    pass

class OutOfTilesError(ValueError):
    """Exception that may be raised when drawing from an empty bag

    Raise this exception when the TileBag is empty upon entering
    into the invocation of TileBag.draw_tiles()
    """
    pass

class ScrabbleTileBag(object):
    """A bag of Tile objects"""

    def __init__(self):
        bag = []
        for letter, num_tiles in num_tiles_by_letter.iteritems():
            for _ in range(num_tiles):
                bag.append(ScrabbleTile(letter))
        random.shuffle(bag)
        self.bag = bag
        self.num_tiles = 100

    def draw_tiles(self, amount):
        if self.num_tiles == 0:
            raise OutOfTilesError("No tiles left")
        tiles = []
        for _ in range(amount):
            if self.num_tiles == 0:
                return tiles
            idx = random.randint(0, self.num_tiles - 1)
            tiles.append(self.bag.pop(idx))
            self.num_tiles -= 1
        return tiles

    def exchange_tiles(self, tiles_to_discard):
        if len(tiles_to_discard) > self.num_tiles:
            raise ExchangeTileError(("'tiles_to_discard': "
                             + "{}".format(len(tiles_to_discard))
                             + " cannot be greater than "
                             + "'num_tiles': {}".format(self.num_tiles)))
        else:
            new_tiles = draw_tiles(len(tiles_to_discard))
            self.bag = self.bag + tiles_to_discard
            random.shuffle(self.bag)
            return new_tiles
    
class ScrabbleTile(object):
    """Represents a Scrabble tile

    Tile is a class representing a Scrabble tile with very limited
    functionality, i.e. getting the value of and/or the letter on
    the tile.
    """

    def __init__(self, letter=None):
        self.letter = letter
        self.value = value_by_letter[letter]

    def __str__(self):
        return "Letter {}; {} points".format(self.letter, self.value)

    def get_letter(self):
        return self.letter

    def get_value(self):
        return self.value

#------------------------------------------------------------------------------
