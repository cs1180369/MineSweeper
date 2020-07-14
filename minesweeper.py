import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells)==self.count :
            return set(self.cells)
        else :
            return set()
    #   raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count==0 :
            return set(self.cells)
        else :
            return set()        
    #   raise NotImplementedError

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells :
            self.cells.remove(cell)
            self.count -=1
            return 1
        else :
            return 0

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells :
            self.cells.remove(cell)
            return 1
        else :
            return 0
    #    raise NotImplementedError


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        count = 0
        self.mines.add(cell)
        for sentence in self.knowledge:
            count+=sentence.mark_mine(cell)
        return count

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        count=0
        self.safes.add(cell)
        for sentence in self.knowledge:
            count+=sentence.mark_safe(cell)
        return count
    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)
        (x,y)=cell
        friends = set()
        for i in range (max(0,x-1),min(x+2,self.height)) :
            for j in range (max(0, y-1), min(y+2, self.width)) :
                if (i,j) != (x,y) :
                    friends.add((i,j))
        self.knowledge.append(Sentence(friends,count))
        self.update()
        new_data = self.inference()
        while new_data:
            for s in new_data:
                self.knowledge.append(s)
            self.update()
            new_data = self.inference()
            pass

    def inference(self):
        new_data = []
        trash = []
        for s1 in self.knowledge:
            if s1.cells == set() :
                trash.append(s1)
                continue
            for s2 in self.knowledge:
                if s2.cells == set() :
                    trash.append(s2)
                    continue 
                if s1!=s2 :
                    if s2.cells.issubset(s1.cells) :
                        diff_cells = s1.cells.difference(s2.cells)
                        diff_count = s1.count - s2.count
                        diff = Sentence(diff_cells,diff_count)
                        if diff not in self.knowledge :
                            new_data.append(diff)
        self.knowledge = [x for x in self.knowledge if x not in trash]
        return new_data

    def update(self):
        counter=1
        while counter:
            counter = 0
            for x in self.knowledge:
                for cell in x.known_safes():
                     counter += self.mark_safe(cell)
                     continue
                for cell in x.known_mines():
                     counter += self.mark_mine(cell) 
            for cell in self.safes:
                counter += self.mark_safe(cell)
            for cell in self.mines:
                counter += self.mark_mine(cell)

    def make_safe_move(self):
        for x in self.safes :
            if x not in self.moves_made :
                return x
        return None
    def make_random_move(self):
        for x in range (0,self.height) :
            for y in range (0,self.width) :
                temp = (x,y)
                if temp not in self.mines and temp not in self.moves_made :
                    return temp
        return None