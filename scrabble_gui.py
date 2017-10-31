import ttk
import time

from Tkinter import *
from collections import namedtuple

from scrabble import ScrabbleBoard

SCORE_AREA_FONT = ("Verdana", 14, "bold")
CLICK_CURSOR = "hand2"

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

        file_menu.add_cascade(label="Reset", command=lambda: self.remove_status(self))
        file_menu.add_separator()
        file_menu.add_cascade(label="Quit", command=self.quit)

        self.menus['file'] = file_menu
        self.menus['main'] = main_menu

    def show_frame(self, cont):
        frame = self.frames[cont]
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
        Frame.__init__(self, parent, bg='#E5E6E8')
        label = Label(self, text="Welcome to Scrabble!", bg='#E5E6E8')
        label.pack(pady=10, padx=10)

        start_button = ttk.Button(self,
                                  text="Play",
                                  command=lambda: controller.show_frame(GamePageFrame),
                                  cursor=CLICK_CURSOR)
        start_button.pack()

        quit_button = ttk.Button(self,
                                 text="Quit",
                                 command=self.quit,
                                 cursor=CLICK_CURSOR)
        quit_button.pack(pady=(10,0))

class GamePageFrame(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent, bg='#E5E6E8')
        self.configure_ui()
        self.controller = controller
    
    def configure_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        label = Label(self, text="This is the game", bg='#E5E6E8')
        label.grid(pady=10, padx=10, row=0, column=0, columnspan=3, sticky="ew")

        back_button = ttk.Button(self,
                                 text="Back to Home",
                                 command=lambda: self.controller.show_frame(WelcomePage))
        back_button.grid(row=1, column=0, columnspan=3)

        quit_button = ttk.Button(self, text="Quit", command=self.quit)
        quit_button.grid(row=2, column=0, columnspan=3)

        # self.rack = RackFrame(self, width=400, height=100, bg='blue')

        self.board = GameBoardFrame(self, height=400, width=400)

        self.score_area = ScoreAreaFrame(self, width=100, height=400, bg='blue')

        self.rack = RackFrame(self, width=400, height=100, bg='blue')

        self.status_bar_frame = Label(self, bg='#F0F1F2', relief=SUNKEN)
        self.status_bar_frame.grid(row=5, column=0, columnspan=3, sticky='ew')

        self.status_bar = Label(self.status_bar_frame, text="This is a status", bg='#F0F1F2')
        self.status_bar.pack(side=LEFT)

        self.control_area = ControlAreaFrame(self, width=100, height=400, bg='blue')

    def board_clicked(self, row, col):
        print("row: {}, col: {}".format(row, col))
        color = self.board.tile_label_by_coords[row, col].cget('bg').lower()
        # print(color)
        if color == 'white':
            # print("changing to blue")
            letter = self.rack.get_selected_letter()
            if letter is not None:
                self.board.tile_label_by_coords[row, col].configure(bg='blue',
                                                                    text=letter)
                self.board.set_letter_played(row, col, letter)
                self.rack.set_letter_played(letter)
        else:
            # print("changing to white")
            # self.board.tile_label_by_coords[row, col].configure(bg='white')
            tile_label = self.board.scrabble_board.base_board[row][col].shorthand()
            self.board.tile_label_by_coords[row, col].configure(bg='white',
                                                                text=tile_label)

    def reset_hand(self):
        print("You reset the hand")
        letters_to_reset = []
        for row_col_list, letter in self.board.letters_played_in_hand.iteritems():
            self.board_clicked(row_col_list[0], row_col_list[1])
            letters_to_reset.append(letter)
        self.rack.reset_hand(letters_to_reset)
        self.board.letters_played_in_hand = {}


class GameBoardFrame(Frame):

    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.rows = 15
        self.cols = 15
        self.board_width = kwargs['width']
        self.scrabble_board = ScrabbleBoard()
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
                label.bind("<Button-1>", lambda e, x=col_pos, y=row_pos: self.parent.board_clicked(y, x))
                label.pack(fill=BOTH, expand=True)
                label.update()
                self.tile_label_by_coords[row_pos, col_pos] = label
                row_frame_list.append(tile)
            row_frame.pack(side=TOP)
            row_frame.update()
            self.tile_frames.append(row_frame_list)
        
        self.grid(padx=10, pady=10, row=3, column=1)

    def set_letter_played(self, row, col, letter):
        self.letters_played_in_hand[row, col] = letter

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

    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.width = kwargs['width']
        self.grid(padx=10, pady=10, row=4, column=1, sticky='nesw')
        self.pack_propagate(False)

        rack_title = Label(self, text="Your Letters", fg='white', bg='blue', font=SCORE_AREA_FONT)
        rack_title.pack(side=TOP)

        self.rack = None

        self.letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        self.draw_rack(self.letters)

        b = ttk.Button(self, text="do it", command=self.change)
        b.pack()
    
    def change(self):
        try:
            self.letters.pop(0)
        except IndexError:
            self.letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        finally:
            self.draw_rack(self.letters)
        # self.set_letters(['A', 'B'])

    def draw_rack(self, letters):
        if self.rack is not None:
            self.rack.destroy()
            self.rack = None
        self.rack = Canvas(self, bg='white', width=300, height=50, borderwidth=0, highlightthickness=0)
        self.rack.pack(side=BOTTOM, pady=(0, 5))
        self.rack_tiles = {}
        self.selected_tile = None

        self.set_letters(letters)

    def set_letters(self, letters):
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
        print("self: {}".format(self))
        print("event: {}".format(event))
        print("tile: {}".format(tile))
        print("letter: {}".format(letter))
        if self.rack_tiles[tile]['selected']:
            self.rack.itemconfigure(tile, fill="blue", outline="black", width=1)
            self.rack_tiles[tile]['selected'] = False
            self.selected_tile = None
            self.selected_letter = None
        else:
            self.rack.itemconfigure(tile, fill="white", outline="blue", width=3)
            self.rack_tiles[tile]['selected'] = True
            if self.selected_tile is not None:
                self.rack.itemconfigure(self.selected_tile, fill="blue", outline="black", width=1)
                self.rack_tiles[self.selected_tile]['selected'] = False
            self.selected_tile = tile
            self.selected_letter = letter

    def get_selected_letter(self):
        return self.selected_letter

    def set_letter_played(self, letter):
        self.select_tile(self, self.selected_tile, letter)
        self.letters.remove(letter)
        self.draw_rack(self.letters)

    def reset_hand(self, letters):
        self.letters = self.letters + letters
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
        outline = self.parent.create_rectangle(final_box, outline="black", fill="blue")

        self.parent.tag_bind(outline,
                             "<ButtonPress-1>",
                             lambda e, box=outline, letter=self.letter: self.controller.select_tile(self,
                                                                                                    box,
                                                                                                    letter))
        self.controller.rack_tiles[outline] = {'selected':False}
        self.parent.tag_bind(canvas_letter,
                             "<ButtonPress-1>",
                             lambda e, box=outline, letter=self.letter: self.controller.select_tile(self,
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
        player1_score = Label(container,
                              text="300",
                              bg='blue',
                              fg='white',
                              font=SCORE_AREA_FONT)
        player1_score.grid(row=1, column=2)

        player2_score_label = Label(container,
                                    text="Computer: ",
                                    bg='blue',
                                    fg='white',
                                    font=SCORE_AREA_FONT)
        player2_score_label.grid(row=2, column=1, sticky='e')
        player2_score = Label(container,
                              text="377",
                              bg='blue',
                              fg='white',
                              font=SCORE_AREA_FONT)
        player2_score.grid(row=2, column=2)

        container.pack()
        self.grid(padx=10, pady=10, row=3, rowspan=2, column=0, sticky='ns')

app = ScrabbleApp()
app.mainloop()