"""
Author:		David Sornberger
Assignment:	Final Project, Question 3: Scrabble
Class:		CS454 - Theory of Computation
Date:		Fall 2017
"""
from word import Word
from scrabble_dfa import DFA
import scrabble
from collections import namedtuple

class ScrabbleAI(object):
    """This is the AI Class portion of scrabble
    
    This will be used to create AI responses to words played
    """
    def __init__(self, dfa, threshold):
        self.dfa = dfa
        self.threshold = threshold

    def find_acceptable_word(self, board, letters):
        """ This functions job is to find an accepting word
        This will be done by looping through all of the coordinates
        that exist in anchor coordinates until a word is found that 
        beats the threshold
        """
        best_score = 0
        best_word = ""
        for coord in board.anchor_coords :
            r = coord[0]
            c = coord[1]
            if not board.player_board[r][c]:
                (word, score) = self.get_word_right(r, c, board, letters, self.get_contiguous_block_left((r, c), board), {}, -1)
                if score > best_score and word:
                    print("New horizontal word, {}, is better than old word, {}.".format(word, best_word))
                    best_score = score
                    best_word = word
                (word, score) = self.get_word_down(r, c, board, letters, self.get_contiguous_block_up((r, c), board), {}, -1)
                if score > best_score and word:
                    print("New vertical word, {}, is better than old word, {}.".format(word, best_word))
                    best_score = score
                    best_word = word
                
        print("Best word in find_acceptable_words is: {}, with a score: {}".format(best_word, best_score))
        return ""   
    def find_words_for_anchor(self, coord, board, letters):
        """ This function finds an acceptable/optimal word for an anchor
        This will be done by trying all of the words that can come out of it
        from right, left, down, and upward directions
        """
        return ""
    def get_contiguous_block_down(self, coord, board):
        """ This is a helper function to find a chunk of letters next to coordinate
        This is done by finding the letters below a coordinate
        """
        #define a word and begin getting contiguous block
        contig_block = ""
        row = coord[0] + 1
        col = coord[1]
        #loop through in downward direction and add to word if not ''
        if row > scrabble.MAX_LENGTH or col > scrabble.MAX_LENGTH or row < 0 or col < 0:
            return ""
        while row < scrabble.MAX_LENGTH and board.player_board[row][col] != '' :
            contig_block += board.player_board[row][col]
            row += 1
        #urn the finished word
        return contig_block

    def get_contiguous_block_right(self, coord, board):
        """ This is a helper function to find a chunk of letters next to coordinate
        This is done by finding the letters to the right of a coordinate
        """
        #define a word and begin getting contiguous block
        contig_block = ""
        row = coord[0]
        col = coord[1] + 1
        if row > scrabble.MAX_LENGTH or col > scrabble.MAX_LENGTH or row < 0 or col < 0:
            return ""
        #loop through in downward direction and add to word if not ''
        while col < scrabble.MAX_LENGTH and board.player_board[row][col] != '':
            contig_block += board.player_board[row][col]
            col += 1
        #return the finished word
        return contig_block
    def get_contiguous_block_up(self, coord, board):
        """ This is a helper function to find a chunk of letters next to coordinate
        This is done by finding the letters above a coordinate
        """
        #define a word and begin getting contiguous block
        contig_block = ""
        row = coord[0] - 1
        col = coord[1]
        if row > scrabble.MAX_LENGTH or col > scrabble.MAX_LENGTH or row < 0 or col < 0:
            return ""
        #loop through in upward direction and add to word if not ''
        while row > 0 and board.player_board[row][col] != '':
            contig_block = board.player_board[row][col] + contig_block
            row -= 1
        #return the finished word
        return contig_block
    def get_contiguous_block_left(self, coord, board):
        """ This is a helper function to find a chunk of letters next to coordinate
        This is done by finding the letters to the left of a coordinate
        """
        #define a word and begin getting contiguous block
        contig_block = ""
        row = coord[0]
        col = coord[1] - 1
        if row > scrabble.MAX_LENGTH or col > scrabble.MAX_LENGTH or row < 0 or col < 0:
            return ""
        #loop through in leftward direction and add to word if not ''
        while col > 0 and board.player_board[row][col] != '':
            contig_block = board.player_board[row][col] + contig_block
            col -= 1
        #return the finished word
        return contig_block

    def get_word_right(self, row, col, board, letters, state, letters_by_coords, end_col):
        """ This function finds a word to the right of a coordinate
        This is done by a depth first search of the dfa with checks at each point
        run into
        """
        #check that letter in letters plus state is in DFA
        #check that if there is a contiguous block up or down, or both, 
        #the created string is accepted in dfa then check if there is a contiguous
        #block to the right, if so check that state + letter + contiguous block exist
        #in the DFA, if they do and it is accepting, then if the score is greater
        #then threshold return it, if not greater than threshold do not. If it is not
        #accepting or not greater than threshold continue the search, with a new entry
        #in letters_by_coords
        if row < 0 or row > scrabble.MAX_LENGTH or col < 0 or col > scrabble.MAX_LENGTH:
            return ("", 0)
        best_score = 0
        best_word = ""
        slice_except = 0
        for letter in letters:
            try:
                self.dfa.dfa[state + letter]
                modified_letter_dict = dict(letters_by_coords)
                modified_letter_dict[(row, col)] = letter
                down = self.get_contiguous_block_down((row, col), board)
                up = self.get_contiguous_block_up((row, col), board)
                right = self.get_contiguous_block_right((row, col), board)
                if down:
                    if up:
                        if not self.dfa.accepts(up + letter + down):
                            continue
                    if not self.dfa.accepts(letter + down):
                        continue
                if up:
                    if not self.dfa.accepts(up + letter):
                        continue
                if right != "":
                    self.dfa.dfa[state + letter + right]
                    letter += right
                    col += len(right)
                if col >= end_col:
                    score = int(board.get_hand_legality_by_score(modified_letter_dict))
                    if score > best_score and state + letter != '':
                        print("New word in dfs, {}, to replace old one, {}, with score: {}, and coordinate: {}, {}".format(state + letter, best_word, score, row, col))
                        best_score = score
                        best_word = state + letter
                    if score >= self.threshold:
                        return (state + letter, score)
                (word, deep_score) = self.get_word_right(row, col + 1, board, letters[:slice_except] + letters[slice_except+1:], state + letter, modified_letter_dict, end_col)
                if deep_score > best_score and word:
                    if deep_score > self.threshold:
                        return (word, deep_score)
                    best_score = deep_score
                    best_word = word
            except KeyError:
                a = 0
            slice_except += 1
        return (best_word, best_score)

    def get_word_down(self, row, col, board, letters, state, letters_by_coords, end_row):    
        """ This function finds a word below a coordinate
        This is done through depth first DFA search with checks at every point
        """
        best_score = 0
        best_word = ""
        slice_except = 0
        for letter in letters:
            try:
                self.dfa.dfa[state + letter]
                modified_letter_dict = dict(letters_by_coords)
                modified_letter_dict[(row, col)] = letter
                left = self.get_contiguous_block_left((row, col), board)
                right = self.get_contiguous_block_right((row, col), board)
                down = self.get_contiguous_block_down((row, col), board)
                if right != "":
                    if left != "":
                        if not self.dfa.accepts(left + letter + right):
                            continue
                    if not self.dfa.accepts(letter + right):
                        continue
                if left != "":
                    if not self.dfa.accepts(left + letter):
                        continue
                if down != "":
                    self.dfa.dfa[state + letter + down]
                    letter += down
                    col += len(right)
                if row >= end_row:
                    score = int(board.get_hand_legality_by_score(modified_letter_dict))
                    if score > best_score and state + letter != '':
                        print("New word in dfs, {}, to replace old one, {}, with score: {}, and coordinate: {}, {}".format(state + letter, best_word, score, row, col))
                        best_score = score
                        best_word = state + letter
                    if score >= self.threshold:
                        return (state+letter, score)
                (word, deep_score) = self.get_word_down(row + 1, col, board, letters[:slice_except] + letters[slice_except+1:], state + letter, modified_letter_dict, end_row)
                if deep_score > best_score:
                    if deep_score > self.threshold:
                        return (word, deep_score)
                    best_score = deep_score
                    best_word = word
            except KeyError:
                print("{} not found as DFA entry".format(state+letter))
            slice_except += 1
        return (best_word, best_score)

    def get_word_left(self, row, col, board, letters, state, letters_by_coords):
        """ This function finds a word to the left of a coordinate
        This is done through backwards iteration to the length of hand
        to search the dfa
        """
        return ""

    def get_word_up(self, row, col, board, letters, state, letters_by_coords):
        """ This function finds a word below a coordinate 
        This is done by iterating in reverse regarding the length of the word
        with the destination being the anchor point and then a DFA search
        """
        return ""
