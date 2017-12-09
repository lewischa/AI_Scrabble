class Word:
    """A logically dumb property bag for a word.

    This class can be used to hold useful information about a word that
    could potentially be used on a Scrabble board. Operator overloads are also
    provided for easy comparison between two word objects, based on each
    object's score.
    """

    def __init__(self, word, letters_by_coord, score):
        self.word = word
        self.letters_by_coord = letters_by_coord
        self.score = score

    def get_word(self):
        return self.word

    def get_letters_by_coord(self):
        return self.letters_by_coord

    def get_score(self):
        return self.score

    #   Built-in method overrides and operator overloads

    def __str__(self):
        """Built-in override for print() method."""

        return "Word: {}, score: {}".format(self.word, self.score)

    def __lt__(self, other_word):
        """self < other_word"""

        return self.score < other_word.get_score()

    def __le__(self, other_word):
        """self <= other_word"""

        return self.score <= other_word.get_score()

    def __ne__(self, other_word):
        """self != other_word"""

        return self.score != other_word.get_score()

    def __eq__(self, other_word):
        """self == other_word"""

        return self.score == other_word.get_score()

    def __ge__(self, other_word):
        """self >= other_word"""

        return self.score >= other_word.get_score()

    def __gt__(self, other_word):
        """self > other_word"""

        return self.score > other_word.get_score()
