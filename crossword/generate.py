import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains:
            var_length = variable.length
            values = self.domains[variable].copy()
            for value in values:
                if var_length != len(value):
                    self.domains[variable].remove(value)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        contradiction = list()
        if self.crossword.overlaps[(x, y)] is not None:
            (i, j) = self.crossword.overlaps[(x, y)]
            for variable in self.domains[x]:
                is_contradict = True
                for var in self.domains[y]:
                    if variable[i] == var[j]:
                        is_contradict = False
                if is_contradict:
                    contradiction.append(variable)

            if contradiction:
                for value in contradiction:
                    self.domains[x].remove(value)
                return True

        return False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = [(x, y) for x in self.domains for y in self.domains if x != y]

        while arcs:
            (x, y) = arcs.pop(0)
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                for val in self.domains:
                    if val != x and val != y:
                        arcs.append((val, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(self.domains) == len(assignment)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # check if all values distinct
        if len(set(assignment.values())) != len(assignment.values()):
            return False

        # check if every value is correct length
        for (var, word) in assignment.items():
            if var.length != len(word):
                return False

        # check if there is any conflict between neighbouring variables
        for var in assignment:
            for neigh in self.crossword.neighbors(var):
                if neigh in assignment:
                    (i, j) = self.crossword.overlaps[(var, neigh)]
                    if assignment[var][i] != assignment[neigh][j]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        rule_out = dict()
        neighbours = self.crossword.neighbors(var)
        for val in self.domains[var]:
            rule_out[val] = 0
            for neigh in neighbours:
                if neigh not in assignment:
                    if self.crossword.overlaps[(var, neigh)] is not None:
                        (i, j) = self.crossword.overlaps[(var, neigh)]
                        for word in self.domains[neigh]:
                            if val[i] != word[j]:
                                rule_out[val] += 1

        sorted_values = sorted(self.domains[var], key=lambda item: rule_out[item])
        return sorted_values

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        not_assigned = dict()
        for var in self.domains:
            if var not in assignment:
                not_assigned[var] = len(self.domains[var])

        sorted_values = sorted(list(not_assigned.values()))
        if len(sorted_values) <= 1:
            return list(not_assigned.keys())[0]
        elif sorted_values[0] != sorted_values[1]:
            wanted = sorted_values[0]
            for (k, v) in not_assigned.items():
                if wanted == v:
                    return k
        else:
            output = dict()
            keys = []
            wanted = sorted_values[0]
            for (k, v) in not_assigned.items():
                if wanted == v:
                    keys.append(k)

            for key in keys:
                output[key] = len(self.crossword.neighbors(key))

            val = sorted(list(output.values()))
            return_output = val[0]
            for (k, v) in output.items():
                if v == return_output:
                    return k

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        variable = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(variable, assignment):
            assignment[variable] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment.copy())
                if result is not None:
                    return result
            assignment.pop(variable)
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
