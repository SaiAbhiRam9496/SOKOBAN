import copy


class Sokoban:
    """
    Pure game logic — zero pygame dependencies.
    Safe for use by renderer (main.py) and RL agents.
    """

    def __init__(self, level):
        self.original_level = [list(row) for row in level]
        self.reset()

    def reset(self):
        self.level = [row[:] for row in self.original_level]
        self.height = len(self.level)
        self.width = max(len(row) for row in self.level)

        # Ensure all rows are padded to equal width
        for row in self.level:
            while len(row) < self.width:
                row.append(' ')

        # Locate player
        self.player_x = 0
        self.player_y = 0
        for y, row in enumerate(self.level):
            for x, tile in enumerate(row):
                if tile in ('@', '+'):
                    self.player_x = x
                    self.player_y = y

        self.history    = []   # list of (level_snapshot, px, py)
        self.move_count = 0
        self.push_count = 0

    # ── Helpers ─────────────────────────────────────────────────────────

    def _get(self, x, y):
        """Return tile at (x,y), '#' if out of bounds."""
        if 0 <= y < self.height and 0 <= x < len(self.level[y]):
            return self.level[y][x]
        return '#'

    def _set(self, x, y, tile):
        self.level[y][x] = tile

    def _snapshot(self):
        self.history.append(([row[:] for row in self.level],
                              self.player_x, self.player_y))

    # ── Public API ───────────────────────────────────────────────────────

    def move(self, dx, dy):
        """Move player by (dx,dy). Returns True if a move was made."""
        nx, ny = self.player_x + dx, self.player_y + dy
        target = self._get(nx, ny)

        if target == '#':
            return False          # wall / out-of-bounds

        pushed = False

        if target in ('$', '*'):  # box in the way
            bx, by = nx + dx, ny + dy
            beyond = self._get(bx, by)

            if beyond not in (' ', '.'):
                return False      # box can't be pushed

            self._snapshot()

            # ① Place box at its new position
            self._set(bx, by, '*' if beyond == '.' else '$')

            # ② Restore tile under box
            #    If box was on a goal ('*'), expose the goal ('.')
            #    If box was on plain floor ('$'), leave floor (' ')
            self._set(nx, ny, '.' if target == '*' else ' ')

            pushed = True

        else:
            self._snapshot()      # plain move

        # ③ Vacate player's current tile
        cur = self._get(self.player_x, self.player_y)
        self._set(self.player_x, self.player_y, '.' if cur == '+' else ' ')

        # ④ Place player at destination
        #    Read the tile NOW — it may have been updated in step ②
        #    e.g. after pushing a box off a goal, tile is '.' not original '*'
        dest_now = self._get(nx, ny)
        self._set(nx, ny, '+' if dest_now == '.' else '@')

        self.player_x  = nx
        self.player_y  = ny
        self.move_count += 1
        if pushed:
            self.push_count += 1

        return True

    def undo(self):
        """Undo the last move. Returns True if successful."""
        if not self.history:
            return False
        snapshot, px, py = self.history.pop()
        self.level    = snapshot
        self.player_x = px
        self.player_y = py
        self.move_count = max(0, self.move_count - 1)
        return True

    def is_completed(self):
        """True when every box is on a goal (no bare '$' remain)."""
        return not any('$' in row for row in self.level)

    # ── RL interface ─────────────────────────────────────────────────────

    def get_state(self):
        """Hashable state for tabular RL: (player_pos, frozenset of box positions)."""
        boxes = frozenset(
            (x, y)
            for y, row in enumerate(self.level)
            for x, tile in enumerate(row)
            if tile in ('$', '*')
        )
        return (self.player_x, self.player_y), boxes

    def count_boxes_on_goals(self):
        return sum(row.count('*') for row in self.level)

    def count_remaining_boxes(self):
        return sum(row.count('$') for row in self.level)
