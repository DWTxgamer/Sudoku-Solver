from itertools import combinations


grid = [
    [' ', '1', '3', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', '5', ' ', ' ', ' ', ' ', '4'],
    ['5', ' ', ' ', ' ', '2', '7', ' ', ' ', '3'],

    [' ', '5', ' ', ' ', '6', ' ', ' ', ' ', ' '],
    ['7', '3', ' ', ' ', ' ', '5', ' ', '2', ' '],
    ['9', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],

    [' ', '7', ' ', ' ', '9', ' ', '8', ' ', '2'],
    ['2', ' ', ' ', ' ', ' ', ' ', '1', '9', ' '],
    [' ', ' ', ' ', ' ', '1', ' ', ' ', ' ', ' '],
]


class Solver:
    DIGITS = set('123456789')

    def __init__(self, ORIGINAL_GRID):
        self.originalGrid = [row[:] for row in ORIGINAL_GRID]
        self.grid = [row[:] for row in ORIGINAL_GRID]

        self.candidates = self._init_candidates()

    def _init_candidates(self):
        candidates = {}

        for r in range(9):
            for c in range(9):
                if self.grid[r][c] != ' ':
                    continue

                candidates[(r, c)] = self.get_cell_candidates(r, c)
        return candidates

    def get_cell_candidates(self, r, c):
        if self.grid[r][c] != ' ':
            return set()

        box_r = r // 3 * 3
        box_c = c // 3 * 3

        blocked = (
            {
                self.grid[r][c2]
                for c2 in range(9)
                if self.grid[r][c2] != ' '
            }
            | {
                self.grid[r2][c]
                for r2 in range(9)
                if self.grid[r2][c] != ' '
            }
            | {
                self.grid[r2][c2]
                for r2 in range(box_r, box_r + 3)
                for c2 in range(box_c, box_c + 3)
                if self.grid[r2][c2] != ' '
            }
        )
        return self.DIGITS - blocked

    def place(self, r, c, digit):
        if (r, c) not in self.candidates:
            return False

        if digit not in self.candidates[(r, c)]:
            return False

        self.grid[r][c] = digit

        del self.candidates[(r, c)]

        box_r = r // 3 * 3
        box_c = c // 3 * 3

        for c2 in range(9):
            if (r, c2) in self.candidates:
                self.candidates[(r, c2)].discard(digit)

        for r2 in range(9):
            if (r2, c) in self.candidates:
                self.candidates[(r2, c)].discard(digit)

        for r2 in range(box_r, box_r + 3):
            for c2 in range(box_c, box_c + 3):
                if (r2, c2) in self.candidates:
                    self.candidates[(r2, c2)].discard(digit)

        return True

    def build_lines(self):
        lines = []

        for r in range(9):
            lines.append([
                (r, c)
                for c in range(9)
            ])

        for c in range(9):
            lines.append([
                (r, c)
                for r in range(9)
            ])

        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                lines.append([
                    (r, c)
                    for r in range(br, br + 3)
                    for c in range(bc, bc + 3)
                ])

        return lines

    def get_missing(self, line):
        present = {
            self.grid[r][c]
            for r, c in line
            if self.grid[r][c] != ' '
        }

        return self.DIGITS - present

    def place_naked_singles(self):
        changed = False

        for cell in list(self.candidates):
            if len(self.candidates[cell]) == 0:
                continue

            if len(self.candidates[cell]) == 1:
                r, c = cell
                digit = next(iter(self.candidates[cell]))

                if self.place(r, c, digit):
                    changed = True

        return changed

    def place_hidden_singles(self):
        changed = False

        for line in self.build_lines():
            missing = self.get_missing(line)

            for digit in missing:
                valid_cells = [
                    cell
                    for cell in line
                    if cell in self.candidates
                    and digit in self.candidates[cell]
                ]

                if len(valid_cells) == 1:
                    r, c = valid_cells[0]

                    if self.place(r, c, digit):
                        changed = True
        return changed

    def eliminate_pairs(self):
        changed = False

        for line in self.build_lines():
            cells = [
                cell
                for cell in line
                if cell in self.candidates
            ]

            for size in (2, 3):
                for group in combinations(cells, size):
                    union = set().union(
                        *(self.candidates[cell] for cell in group)
                    )

                    if len(union) != size:
                        continue

                    for cell in cells:
                        if cell in group:
                            continue

                        old = self.candidates[cell]
                        new = old - union

                        if new != old:
                            self.candidates[cell] = new
                            changed = True
        return changed

    def eliminate_hidden_pairs(self):
        changed = False

        for line in self.build_lines():
            cells = [
                cell
                for cell in line
                if cell in self.candidates
            ]

            missing = self.get_missing(line)

            for d1, d2 in combinations(missing, 2):
                cells_d1 = {
                    cell
                    for cell in cells
                    if d1 in self.candidates[cell]
                }

                cells_d2 = {
                    cell
                    for cell in cells
                    if d2 in self.candidates[cell]
                }

                if (
                    len(cells_d1) == 2
                    and cells_d1 == cells_d2
                ):
                    pair_cells = cells_d1

                    for cell in pair_cells:
                        old = self.candidates[cell]
                        new = old & {d1, d2}

                        if new != old:
                            self.candidates[cell] = new
                            changed = True
        return changed

    def eliminate_pointing_pairs(self):
        changed = False

        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                box_cells = [
                    (r, c)
                    for r in range(br, br + 3)
                    for c in range(bc, bc + 3)
                    if (r, c) in self.candidates
                ]

                for digit in self.DIGITS:
                    possible = [
                        cell
                        for cell in box_cells
                        if digit in self.candidates[cell]
                    ]

                    if len(possible) < 2:
                        continue

                    rows = {r for r, c in possible}
                    cols = {c for r, c in possible}

                    if len(rows) == 1:
                        row = next(iter(rows))

                        for c in range(9):
                            cell = (row, c)

                            if cell in box_cells:
                                continue

                            if cell in self.candidates:
                                if digit in self.candidates[cell]:
                                    self.candidates[cell].remove(digit)
                                    changed = True

                    if len(cols) == 1:
                        col = next(iter(cols))

                        for r in range(9):
                            cell = (r, col)

                            if cell in box_cells:
                                continue

                            if cell in self.candidates:
                                if digit in self.candidates[cell]:
                                    self.candidates[cell].remove(digit)
                                    changed = True
        return changed

    def eliminate_x_wing(self):
        changed = False

        for digit in self.DIGITS:
            row_positions = {}

            for r in range(9):
                cols = [
                    c
                    for c in range(9)
                    if (r, c) in self.candidates
                    and digit in self.candidates[(r, c)]
                ]

                if len(cols) == 2:
                    row_positions[r] = tuple(cols)

            for r1, r2 in combinations(row_positions, 2):
                cols1 = row_positions[r1]
                cols2 = row_positions[r2]

                if cols1 != cols2:
                    continue

                c1, c2 = cols1

                for r in range(9):
                    if r in (r1, r2):
                        continue

                    for c in (c1, c2):
                        cell = (r, c)

                        if (
                            cell in self.candidates
                            and digit in self.candidates[cell]
                        ):
                            self.candidates[cell].remove(digit)
                            changed = True

            col_positions = {}

            for c in range(9):
                rows = [
                    r
                    for r in range(9)
                    if (r, c) in self.candidates
                    and digit in self.candidates[(r, c)]
                ]

                if len(rows) == 2:
                    col_positions[c] = tuple(rows)

            for c1, c2 in combinations(col_positions, 2):
                rows1 = col_positions[c1]
                rows2 = col_positions[c2]

                if rows1 != rows2:
                    continue

                r1, r2 = rows1

                for c in range(9):
                    if c in (c1, c2):
                        continue

                    for r in (r1, r2):
                        cell = (r, c)

                        if (
                            cell in self.candidates
                            and digit in self.candidates[cell]
                        ):
                            self.candidates[cell].remove(digit)
                            changed = True
        return changed

    def eliminate_y_wing(self):
        changed = False

        def sees(cell1, cell2):
            r1, c1 = cell1
            r2, c2 = cell2

            same_row = r1 == r2
            same_col = c1 == c2
            same_box = (
                r1 // 3 == r2 // 3
                and c1 // 3 == c2 // 3
            )

            return same_row or same_col or same_box

        bivalue_cells = [
            cell
            for cell in self.candidates
            if len(self.candidates[cell]) == 2
        ]

        for pivot in bivalue_cells:
            pivot_candidates = self.candidates[pivot]

            for wing1, wing2 in combinations(
                [
                    cell
                    for cell in bivalue_cells
                    if cell != pivot
                    and sees(pivot, cell)
                ],
                2
            ):
                wing1_candidates = self.candidates[wing1]
                wing2_candidates = self.candidates[wing2]

                common = (
                    wing1_candidates
                    & wing2_candidates
                )

                if len(common) != 1:
                    continue

                shared = next(iter(common))

                wing1_unique = (
                    wing1_candidates - {shared}
                )

                wing2_unique = (
                    wing2_candidates - {shared}
                )

                if len(wing1_unique) != 1:
                    continue

                if len(wing2_unique) != 1:
                    continue

                a = next(iter(wing1_unique))
                b = next(iter(wing2_unique))

                if {a, b} != pivot_candidates:
                    continue

                for target in self.candidates:

                    if target in (pivot, wing1, wing2):
                        continue

                    if not sees(target, wing1):
                        continue

                    if not sees(target, wing2):
                        continue

                    if shared in self.candidates[target]:
                        self.candidates[target].remove(shared)
                        changed = True
        return changed


    def nakedDeduction(self):
        changed = False

        if self.eliminate_pairs():
            changed = True

        if self.eliminate_hidden_pairs():
            changed = True

        if self.eliminate_pointing_pairs():
            changed = True

        if self.eliminate_x_wing():
            changed = True

        if self.eliminate_y_wing():
            changed = True

        if self.place_naked_singles():
            changed = True

        if self.place_hidden_singles():
            changed = True

        return changed

    def crossHatch(self):
        changed = False

        for digit in '123456789':
            placed = [
                (r, c)
                for r in range(9)
                for c in range(9)
                if self.grid[r][c] == digit
            ]

            for si in range(0, 9, 3):
                for sj in range(0, 9, 3):

                    if any(
                        self.grid[r][c] == digit
                        for r in range(si, si + 3)
                        for c in range(sj, sj + 3)
                    ):
                        continue

                    valid = []

                    for r in range(si, si + 3):
                        for c in range(sj, sj + 3):

                            if self.grid[r][c] != ' ':
                                continue

                            blockedRow = any(
                                xR == r
                                for xR, xC in placed
                            )

                            blockedColumn = any(
                                xC == c
                                for xR, xC in placed
                            )

                            if not blockedRow and not blockedColumn:
                                valid.append((r, c))

                    if len(valid) == 1:
                        r, c = valid[0]

                        if self.place(r, c, digit):
                            changed = True

                            placed.append((r, c))
        return changed

    def has_contradiction(self):
        for cell, candidates in self.candidates.items():
            if len(candidates) == 0:
                return True

        for line in self.build_lines():
            values = [
                self.grid[r][c]
                for r, c in line
                if self.grid[r][c] != ' '
            ]

            if len(values) != len(set(values)):
                return True

        for line in self.build_lines():
            missing = self.get_missing(line)

            for digit in missing:
                possible = [
                    cell
                    for cell in line
                    if cell in self.candidates
                    and digit in self.candidates[cell]
                ]

                if not possible:
                    return True

        return False

    def is_solved(self):
        return not self.candidates

    def controler(self):
        while True:
            if self.has_contradiction():
                print("Contradiction detected.")
                return False

            if self.is_solved():
                break

            changed = False

            if self.crossHatch():
                changed = True

            if self.nakedDeduction():
                changed = True

            if not changed:
                break

        if self.is_solved():
            print("Solved!")
            return self.grid

        print("Solver got stuck.")
        return self.grid


if __name__ == '__main__':
    app = Solver(grid)
    app.controler()
