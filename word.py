from collections import namedtuple

#   value_by_letter is the value of a Scrabble tile based on its letter.
#   This is already defined in tile.py, no need to redefine it here.
from tile import value_by_letter

Coordinate = namedtuple('Coordinate', 'row, col')

class Word:
    """A relatively dumb property bag for a word.

    This class can be used to hold useful information about a word that
    could potentially be used on a Scrabble board.
    """

    def __init__(self, word, orientation, coordinate):
        self.word_str = word.lower()
        self.score = self._calculate_score()
        self.orientation = orientation

        #   NOTE: `coordinate` should be passed in as a tuple, in the form of
        #           (row, col)
        self.coordinate = Coordinate(row=coordinate[0], col=coordinate[1])

    def _calculate_score(self):
        """Calculate the score of a word based only on its letters."""

        score = 0
        for letter in self.word_str:
            score += value_by_letter[letter]
        return score
