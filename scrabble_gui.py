import sys
import time

import ttk
from Tkinter import *
from collections import namedtuple

from scrabble import ScrabbleBoard
from tile import ScrabbleTileBag
from player import Player
from scrabble_ai import ScrabbleAI
SCORE_AREA_FONT = ("Verdana", 14, "bold")
CLICK_CURSOR = "hand2"
INVALID_COLOR = "#ff0000"
VALID_COLOR = "#009300"
COLORS = {
    'background': "#E5E6E8"
}
AI_THRESHOLD = {
    0: 10,
    1: 25,
    2: 50,
    3: 1000
}

class ScrabbleApp(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        Tk.wm_title(self, "Scrabble")
        self.menus = {}
        self.create_menu()

        container = Frame(self)
        container.pack(side=TOP, fill=BOTH, expand=True)

        self.frames = {}
        self.active_frame = None
        for each in (WelcomePage, GamePageFrame):
            frame = each(container, self)
            self.frames[each] = frame
            frame.grid(row=0, column=0, sticky="NESW")

        self.show_frame(WelcomePage)
        self.toggle = True

    def create_menu(self):
        main_menu = Menu(self)
        self.config(menu=main_menu)

        file_menu = Menu(main_menu)
        main_menu.add_cascade(label="File", menu=file_menu)

        file_menu.add_cascade(label="Reset",
                              command=lambda: self.remove_status(self))
        file_menu.add_separator()
        file_menu.add_cascade(label="Quit", command=self.quit)

        self.menus['file'] = file_menu
        self.menus['main'] = main_menu

    def show_frame(self, cont, threshold=None):
        frame = self.frames[cont]
        if threshold:
            frame.set_threshold(threshold)
        frame.tkraise()
        self.active_frame = cont
        reset_option_idx = self.menus['file'].index('Reset')
        if cont is GamePageFrame:
            self.menus['file'].entryconfig(reset_option_idx, state="normal")
        else:
            self.menus['file'].entryconfig(reset_option_idx, state="disabled")

    def remove_status(event, self):
        for key, child in self.children.iteritems():
            for obj in child.winfo_children():
                if isinstance(obj, GamePageFrame):
                    if self.toggle:
                        # obj.status_bar.pack_forget()
                        obj.status_bar.configure(text="Changed")
                        self.toggle = False
                    else:
                        # obj.status_bar.pack(side=LEFT)
                        obj.status_bar.configure(text="This is a status")
                        self.toggle = True

class WelcomePage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent, bg=COLORS['background'])
        label = Label(self,
                      text="Welcome to Scrabble!",
                      bg=COLORS['background'])
        label.pack(pady=10, padx=10)
        self.easy = IntVar()
        self.medium = IntVar()
        self.hard = IntVar()
        self.master = IntVar()
        self.checkbox_handles = [self.easy, self.medium, self.hard, self.master]

        start_button = ttk.Button(self,
                                  text="Play",
                                  command=lambda: \
                                    controller.show_frame(
                                        GamePageFrame,
                                        threshold=\
                                            AI_THRESHOLD[
                                                self.get_checked_index()
                                            ]),
                                  cursor=CLICK_CURSOR)
        start_button.pack()

        difficulty_frame = Frame(self, width=100, bg=COLORS['background'])
        difficulty_frame.pack()

        easy_checkbox = ttk.Checkbutton(
                            difficulty_frame,
                            text="Easy",
                            variable=self.easy,
                            command=lambda selected=0: \
                                self.toggle_checkboxes(selected))
        medium_checkbox = ttk.Checkbutton(
                            difficulty_frame,
                            text="Medium",
                            variable=self.medium,
                            command=lambda selected=1: \
                                self.toggle_checkboxes(selected))
        hard_checkbox = ttk.Checkbutton(
                            difficulty_frame,
                            text="Hard",
                            variable=self.hard,
                            command=lambda selected=2: \
                                self.toggle_checkboxes(selected))
        master_checkbox = ttk.Checkbutton(
                            difficulty_frame,
                            text="Master",
                            variable=self.master,
                            command=lambda selected=3: \
                                self.toggle_checkboxes(selected))
        easy_checkbox.pack(anchor="w")
        medium_checkbox.pack(anchor="w")
        hard_checkbox.pack(anchor="w")
        master_checkbox.pack(anchor="w")
        self.easy.set(1)

        quit_button = ttk.Button(self,
                                 text="Quit",
                                 command=self.quit,
                                 cursor=CLICK_CURSOR)
        quit_button.pack(pady=(10,0))

    def toggle_checkboxes(self, selected):
        for i, handle in enumerate(self.checkbox_handles):
            if i != selected:
                handle.set(0)

    def get_checked_index(self):
        for i, handle in enumerate(self.checkbox_handles):
            if handle.get() == 1:
                return i

class GamePageFrame(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent, bg=COLORS['background'])
        self.configure_ui()
        self.controller = controller

    def configure_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        label = Label(self, text="This is the game", bg=COLORS['background'])
        label.grid(pady=10, padx=10, row=0, column=0, columnspan=3, sticky="ew")

        back_button = ttk.Button(self,
                                 text="Back to Home",
                                 command=lambda: \
                                    self.controller.show_frame(WelcomePage))
        back_button.grid(row=1, column=0, columnspan=3)

        quit_button = ttk.Button(self, text="Quit", command=self.quit)
        quit_button.grid(row=2, column=0, columnspan=3)

        self.board = GameBoardFrame(self, height=400, width=400)

        self.score_area = ScoreAreaFrame(self, width=100, height=400, bg='blue')

        self.rack = RackFrame(self, self.board.human.get_letters(),
                              width=400, height=100, bg='blue')

        self.status_bar_frame = Label(self, bg='#F0F1F2', relief=SUNKEN)
        self.status_bar_frame.grid(row=5, column=0, columnspan=3, sticky='ew')

        self.status_bar = Label(self.status_bar_frame, bg='#F0F1F2')
        self.status_bar.pack(side=LEFT)

        self.control_area = ControlAreaFrame(self, width=100,
                                             height=400, bg='blue')
    def set_threshold(self, threshold):
        self.board.set_threshold(threshold)

    def set_word_status(self, score=0, reset=False):
        if reset:
            self.status_bar.config(text="")
        elif score:
            self.status_bar.config(
                text="Valid word. Value is: {}".format(score), fg=VALID_COLOR)
        else:
            self.status_bar.config(
                text="Invalid word.", fg=INVALID_COLOR)

    def board_clicked(self, row, col):
        color = self.board.tile_label_by_coords[row, col].cget('bg').lower()
        if self.board.scrabble_board.is_available(row, col):
            #   The square at row, col is available (i.e. no tile is currently
            #   placed there)
            letter = self.rack.get_selected_letter()
            if letter is not None:
                self.board.tile_label_by_coords[row, col].configure(bg='blue',
                                                                    text=letter)
                self.board.set_letter_played(row, col, letter)
                letters_by_coord = {
                    coord: letter.lower()
                    for coord, letter
                    in self.board.letters_played_in_hand.iteritems()
                }
                score = self.board.scrabble_board.get_hand_legality_by_score(
                            letters_by_coord)
                self.set_word_status(score)
                self.rack.set_letter_played(letter)
                self.board.scrabble_board.set_availability(row, col, False)
        elif not self.board.scrabble_board.is_played(row, col):
            #   The square at row, col is not available (i.e. a tile is occupying
            #   the position), but it's part of the current hand and hasn't
            #   been 'played' yet.
            tile_label = self.board.scrabble_board.base_board[row][col].shorthand()
            self.board.tile_label_by_coords[row, col].configure(bg='white',
                                                                text=tile_label)
            self.board.scrabble_board.set_availability(row, col, True)
            removed_letter = self.board.letters_played_in_hand[row, col]
            self.board.remove_letter_at_coord(row, col)
            letters_by_coord = {
                coord: letter.lower()
                for coord, letter
                in self.board.letters_played_in_hand.iteritems()
            }
            score = self.board.scrabble_board.get_hand_legality_by_score(
                        letters_by_coord)
            self.set_word_status(score)
            self.rack.return_letter(removed_letter)

    def place_word(self, letters_by_coord):
        for key, value in letters_by_coord.iteritems():
            row, col = key
            color = self.board.tile_label_by_coords[row, col].cget('bg').lower()
            self.board.tile_label_by_coords[row, col].configure(bg='blue',
                                                                text=value.upper())
            self.board.set_letter_played(row, col, value.upper())
            self.board.scrabble_board.set_availability(row, col, False)
        self.board.scrabble_board.play_hand(letters_by_coord)
            
    def human_play_hand(self):
        letters_by_coord = self.board.get_letters_by_coord()
        letters_by_coord = {
            coord: letter.lower()
            for coord, letter in letters_by_coord.iteritems()
        }
        score, letters = self.board.human.play_hand(
                            letters_by_coord=letters_by_coord)
        if not score:
            self.reset_hand()
        else:
            self.score_area.set_human_score(self.board.human.get_score())
            self.set_word_status(reset=True)
            self.board.reset_letters_played()
            self.rack.reset_letters(letters)
            self.rack.draw_rack(letters)
	    word = self.board.scrabble_ai.play_hand()
            self.board.scrabble_board.play_hand(word.get_letters_by_coord())
            self.place_word(word.get_letters_by_coord())
            self.score_area.set_ai_score(self.board.scrabble_ai.get_score())
            print("Score: {}".format(score))

    def reset_hand(self):
        print("You reset the hand")
        letters_to_reset = []
        coords_to_reset = []
        print(self.board.letters_played_in_hand)
        for (row, col), letter in self.board.letters_played_in_hand.iteritems():
            coords_to_reset.append((row, col))
            # self.board_clicked(row_col_list[0], row_col_list[1])
            letters_to_reset.append(letter)
        for coord in coords_to_reset:
            self.board_clicked(coord[0], coord[1])
        # self.rack.reset_hand(letters_to_reset)
        self.board.reset_letters_played()
        self.set_word_status(reset=True)


class GameBoardFrame(Frame):

    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.rows = 15
        self.cols = 15
        self.board_width = kwargs['width']
        self.scrabble_board = ScrabbleBoard()
        self.tile_bag = ScrabbleTileBag()
        self.human = Player(self.scrabble_board, self.tile_bag)
        self.scrabble_ai = ScrabbleAI(self.scrabble_board, self.tile_bag, self.scrabble_board.dfa, 20)
        self.tile_frames = []
        self.tile_label_by_coords = {}
        self.letters_played_in_hand = {}

        for row_pos, row in enumerate(self.scrabble_board.base_board):
            row_frame = Frame(self, width=self.board_width, bg='blue')
            row_frame_list = []
            for col_pos, square in enumerate(row):
                tile = Frame(row_frame,
                             width=(self.board_width / self.cols) + 10,
                             height=(self.board_width / self.cols) + 10,
                             highlightbackground='black',
                             highlightcolor='black',
                             highlightthickness=1,
                             bd=0)
                tile.pack(side=LEFT)
                tile.pack_propagate(False)
                tile.update()

                if square.shorthand() == '  ':
                    square_text = '   '
                else:
                    square_text = square.shorthand()
                label = Label(tile, text=square_text)
                label.bind("<Button-1>",
                           lambda e, x=col_pos, y=row_pos: \
                                self.parent.board_clicked(y, x))
                label.pack(fill=BOTH, expand=True)
                label.update()
                self.tile_label_by_coords[row_pos, col_pos] = label
                row_frame_list.append(tile)
            row_frame.pack(side=TOP)
            row_frame.update()
            self.tile_frames.append(row_frame_list)

        self.grid(padx=10, pady=10, row=3, column=1)

    def set_threshold(self, threshold):
        self.scrabble_ai.threshold = threshold
        print("In GameBoardFrame, setting threshold to {}".format(threshold))

    def set_letter_played(self, row, col, letter):
        self.letters_played_in_hand[row, col] = letter
        self.scrabble_board.set_letter(row, col, letter)

    def reset_letters_played(self):
        self.letters_played_in_hand = {}

    def get_letters_by_coord(self):
        return self.letters_played_in_hand

    def remove_letter_at_coord(self, row, col):
        del self.letters_played_in_hand[row, col]

    def callback(self, row, col):
        # print("row: {}, col: {}".format(row, col))
        # color = self.tile_label_by_coords[row, col].cget('bg').lower()
        # print(color)
        # if color == 'white':
        #     print("changing to blue")
        #     # if self.rack.get_selected_letter() is not None:
        #     self.tile_label_by_coords[row, col].configure(bg='blue')
        # else:
        #     print("changing to white")
        #     self.tile_label_by_coords[row, col].configure(bg='white')
        pass

class RackFrame(Frame):

    def __init__(self, parent, letters, **kwargs):
        Frame.__init__(self, parent, **kwargs)
        self.letters = letters
        self.width = kwargs['width']
        self.grid(padx=10, pady=10, row=4, column=1, sticky='nesw')
        self.pack_propagate(False)

        rack_title = Label(self, text="Your Letters", fg='white',
                           bg='blue', font=SCORE_AREA_FONT)
        rack_title.pack(side=TOP)

        self.rack = None

        # self.letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        self.draw_rack(self.letters)

    #     b = ttk.Button(self, text="do it", command=self.change)
    #     b.pack()
    #
    # def change(self):
    #     try:
    #         self.letters.pop(0)
    #     except IndexError:
    #         self.letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    #     finally:
    #         self.draw_rack(self.letters)
    #     # self.set_letters(['A', 'B'])

    def draw_rack(self, letters):
        letters = [letter.upper() for letter in letters]
        if self.rack is not None:
            self.rack.destroy()
            self.rack = None
        self.rack = Canvas(self, bg='white', width=300,
                           height=50, borderwidth=0, highlightthickness=0)
        self.rack.pack(side=BOTTOM, pady=(0, 5))
        self.rack_tiles = {}
        self.selected_tile = None

        self.draw_letters(letters)

    def reset_letters(self, letters):
        self.letters = letters

    def draw_letters(self, letters):
        print("Drawing letters: {}".format(letters))
        print("self.letters: {}".format(self.letters))
        #   Leftmost start position: 17
        #   Rightmost start position: 287
        Dimension = namedtuple('Dimension', 'box_size offset')
        dimensions_by_font_size = {
            24: Dimension(box_size=29, offset=30),
            28: Dimension(box_size=34, offset=15)
        }

        self.rack_tiles = {}

        FONT_SIZE = 28

        for i, letter in enumerate(letters):
            x_start = ((i + 1)
                      * dimensions_by_font_size[FONT_SIZE].box_size
                      + dimensions_by_font_size[FONT_SIZE].offset)
            tile = RackTile(self.rack,
                            self,
                            x_start,
                            25,
                            letter,
                            ("Verdana", FONT_SIZE))

    def select_tile(self, event, tile, letter):
        if self.rack_tiles[tile]['selected']:
            self.rack.itemconfigure(tile, fill="blue", outline="black", width=1)
            self.rack_tiles[tile]['selected'] = False
            self.selected_tile = None
            self.selected_letter = None
        else:
            self.rack.itemconfigure(tile, fill="white", outline="blue", width=3)
            self.rack_tiles[tile]['selected'] = True
            if self.selected_tile is not None:
                self.rack.itemconfigure(self.selected_tile,
                                        fill="blue", outline="black", width=1)
                self.rack_tiles[self.selected_tile]['selected'] = False
            self.selected_tile = tile
            self.selected_letter = letter

    def get_selected_letter(self):
        return self.selected_letter

    def set_letter_played(self, letter):
        self.select_tile(self, self.selected_tile, letter)
        print("self.letters before removal: {}".format(self.letters))
        self.letters.remove(letter.lower())
        print("self.letters after removal: {}".format(self.letters))
        self.draw_rack(self.letters)

    def reset_hand(self, letters):
        letters = [letter.lower() for letter in letters]
        print("self.letters before reset: {}".format(self.letters))
        self.letters = self.letters + letters
        print("self.letters after reset: {}".format(self.letters))
        self.draw_rack(self.letters)

    def return_letter(self, removed_letter):
        self.letters += [removed_letter.lower()]
        self.draw_rack(self.letters)


class RackTile(Canvas):
    #   Arguments
    #
    #   parent -- parent canvas
    #   controller -- controlling class of parent canvas
    #   x_start -- horizontal start position
    #   y_start -- vertical start position
    #   letter -- letter associated with this RackTile
    #   font -- font to be used

    def __init__(self, parent, controller,
                 x_start, y_start, letter, font, **kwargs):
        Canvas.__init__(self, parent, **kwargs)
        self.parent = parent
        self.controller = controller
        self.x_start = x_start
        self.y_start = y_start
        self.letter = letter
        self.font = font
        self.selected = False

        canvas_letter = self.parent.create_text(self.x_start,
                                                self.y_start,
                                                text=self.letter,
                                                font=self.font)
        temp_box = self.parent.bbox(canvas_letter)
        final_box = self.get_box_size(temp_box)
        outline = self.parent.create_rectangle(final_box,
                                               outline="black",
                                               fill="blue")

        self.parent.tag_bind(outline, "<ButtonPress-1>",
                             lambda e, box=outline, letter=self.letter: \
                                self.controller.select_tile(self,
                                                            box,
                                                            letter))
        self.controller.rack_tiles[outline] = {'selected':False}
        self.parent.tag_bind(canvas_letter, "<ButtonPress-1>",
                             lambda e, box=outline, letter=self.letter: \
                                self.controller.select_tile(self,
                                                            box,
                                                            letter))
        self.parent.tag_raise(canvas_letter, outline)

    def get_box_size(self, box):
        x1, y1, x2, y2 = box
        width = x2 - x1
        height = y2 - y1
        if width >= height:
            final_side_length = width
        else:
            final_side_length = height

        x_delta = (final_side_length - width) / 2
        y_delta = (final_side_length - height) / 2

        x2 = x1 + final_side_length
        y2 = y1 + final_side_length

        return (x1 - x_delta, y1 - y_delta, x2 - x_delta, y2 - y_delta)

    def is_selected(self):
        return self.selected

class ControlAreaFrame(Frame):

    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)

        container = Frame(self, bg='blue')

        reset_hand_button = ttk.Button(self,
                                       text="Reset Hand",
                                       command=parent.reset_hand,
                                       cursor=CLICK_CURSOR)
        reset_hand_button.grid(pady=25, row=0)

        play_hand_button = ttk.Button(self,
                                      text="Play Hand",
                                      command=parent.human_play_hand,
                                      cursor=CLICK_CURSOR)
        play_hand_button.grid(pady=25, row=1)

        self.grid(padx=10, pady=10, row=3, rowspan=2, column=2, sticky='ns')

    # def toggle_reset_hand_button(self):

class ScoreAreaFrame(Frame):

    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

        container = Frame(self, bg='blue')

        current_scores_label = Label(container,
                                     text="Current Scores",
                                     bg='blue',
                                     fg='white',
                                     font=SCORE_AREA_FONT)
        current_scores_label.grid(pady=25, row=0, column=1,
                                  columnspan=2, sticky='ew')

        player1_score_label = Label(container,
                                    text="Player 1: ",
                                    bg='blue',
                                    fg='white',
                                    font=SCORE_AREA_FONT)
        player1_score_label.grid(row=1, column=1, sticky='e')
        self.player1_score = Label(container,
                                   text="0",
                                   bg='blue',
                                   fg='white',
                                   font=SCORE_AREA_FONT)
        self.player1_score.grid(row=1, column=2)

        player2_score_label = Label(container,
                                    text="Computer: ",
                                    bg='blue',
                                    fg='white',
                                    font=SCORE_AREA_FONT)
        player2_score_label.grid(row=2, column=1, sticky='e')
        self.player2_score = Label(container,
                                   text="377",
                                   bg='blue',
                                   fg='white',
                                   font=SCORE_AREA_FONT)
        self.player2_score.grid(row=2, column=2)

        container.pack()
        self.grid(padx=10, pady=10, row=3, rowspan=2, column=0, sticky='ns')

    def set_human_score(self, score):
        self.player1_score.config(text=score)

    def set_ai_score(self, score):
        self.player2_score.config(text=score)

def main():
    app = ScrabbleApp()
    app.mainloop()
