import string
import itertools

from sets import Set

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
    'z':10
}

class DFA(object):
    """The DFA used for Scrabble

    The DFA is used to determine whether or not a word is legal in the game of
    Scrabble.
    """
    def __init__(self):
        self.dfa = self.build_dfa()

    def build_dfa(self):
        words_file = "words.txt"
        dfa = {}
        dfa[""] = {}
        for letter in string.ascii_lowercase:
            dfa[""][letter] = letter

        with open(words_file, 'r') as words:
            for word in words:
                dfa  = self.add_word_to_dfa(dfa, word.strip())
        return dfa

    def add_word_to_dfa(self, dfa, word):
        current_state = ""
        for letter in word:
            try:
                state_transitions = dfa[current_state]
            except KeyError:
                dfa[current_state] = {}
                dfa[current_state][letter] = current_state + letter
                current_state = current_state + letter
            else:
                try:
                    current_state = state_transitions[letter]
                except KeyError:
                    dfa[current_state][letter] = current_state + letter
                    current_state = current_state + letter
        try:
            dfa[current_state]
            dfa[current_state]['accept'] = True
        except KeyError:
            dfa[current_state] = {'accept':True}
        return dfa

    def accepts(self, word):
        #   Make sure the word is lowercase -- that is how the DFA is built
        word = word.lower()
        print("Word: {}".format(word))
        if word in self.dfa:
            return 'accept' in self.dfa[word]
        return False
