"""
Author:         Chad Lewis
Assignment:     Final Project, Question 3: Scrabble
Class:          CS 454 - Theory of Computation
Date:           Fall 2017
"""

import string
import itertools

from sets import Set
# from tile import Tile, TileBag, ExchangeTileError, OutOfTilesError

# dfa = {
#   -1:{},
#   0:{
#       'a':1,
#       'b':2,
#       'c':3,
#       'd':4,
#       'e':5,
#       'f':6,
#       'g':7,
#       'h':8,
#       'i':9,
#       'j':10,
#       'k':11,
#       'l':12,
#       'm':13,
#       'n':14,
#       'o':15,
#       'p':16,
#       'q':17,
#       'r':18,
#       's':19,
#       't':20,
#       'u':21,
#       'v':22,
#       'w':23,
#       'x':24,
#       'y':25,
#       'z':26,
#       'accept':False
#   },
#   1:{

#   }
# }

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

def calc_word_value(word):
    score = 0
    return reduce((lambda score, value: score + value),
                  [value_by_letter[l] for l in word])

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
        dfa[0] = {}
        next_state = 1
        for letter in string.ascii_lowercase:
            dfa[0][letter] = next_state
            next_state += 1

        with open(words_file, 'r') as words:
            for word in words:
                dfa, next_state = self.add_word_to_dfa(dfa,
                                                       word.strip(),
                                                       next_state)
        return dfa

    def add_word_to_dfa(self, dfa, word, next_state):
        current_state = 0
        for letter in word:
            try:
                state_transitions = dfa[current_state]
            except KeyError:
                dfa[current_state] = {}
                dfa[current_state][letter] = next_state
                current_state = next_state
                next_state += 1
            else:
                try:
                    current_state = state_transitions[letter]
                except KeyError:
                    dfa[current_state][letter] = next_state
                    current_state = next_state
                    next_state += 1
        try:
            dfa[current_state]
            dfa[current_state]['accept'] = True
        except KeyError:
            dfa[current_state] = {'accept':True}
        return dfa, next_state

    def accepts(self, word):
        #   Make sure the word is lowercase -- that is how the DFA is built
        word = word.lower()
        current_state = 0
        for letter in word:
            try:
                current_state = self.dfa[current_state][letter]
            except KeyError:
                return False
        try:
            is_accept = self.dfa[current_state]['accept']
        except KeyError:
            is_accept = False
        finally:
            return is_accept

#--------------------------------------------
#   Everything below is unnecessary for the gui version of the game,
#   but keeping in for reference when useing TileBag and things later

def word_check_loop(dfa):
    word = raw_input("Enter a word to check (q to quit): ")
    while word != 'q':
        if accepts(dfa, word):
            print("{} is acceptable.".format(word))
            print("Score would be: {}".format(calc_word_value(word)))
        else:
            print("{} is unacceptable.".format(word))
        word = raw_input("Enter another word to check (q to quit): ")

def gen_words(dfa, rack):
    """Generate legal words

    Generate all legal words that can be formed from the letters in the
    'rack' such that all words begin with the letter located at
    'rack[idx]'.
    """
    words = Set()
    letters = ''.join([rack[i].get_letter() for i in range(len(rack))])
    for i in range(2, len(rack) + 1):
        for word in itertools.imap(''.join, itertools.product(letters,
                                                              repeat=i)):
            if word not in words:
                if accepts(dfa, word):
                    words.add(word)
    #   HANDLE BLANKS FOR THE LOVE OF GOD <**************************========================-------------------------
    return words

def gen_words_loop(dfa):
    tbag = TileBag()
    while True:
        try:
            rack = tbag.draw_tiles(7)
            letters = ''.join([rack[i].get_letter() for i in range(len(rack))])
            print("Current letters: '{}'".format(letters))
            words = gen_words(dfa, rack)
            print("{} words were legally generated!".format(len(words)))
            dummy = raw_input("Press any key to continue: ")
        except OutOfTilesError:
            break

# def main():
#     dfa = build_dfa()
#     gen_words_loop(dfa)
