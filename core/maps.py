# Original Sokoban levels by Thinking Rabbit (1988)
# Parsed directly from: github.com/lieberkind/sokoban (raw/elm/original-levels.txt)
# Curated selection: 4 Easy · 3 Medium · 3 Hard

# fmt: off
_RAW = """
    #####
    #   #
    #$  #
  ###  $##
  #  $ $ #
### # ## #   ######
#   # ## #####  ..#
# $  $          ..#
##### ### #@##  ..#
    #     #########
    #######
TITLE:Level 1:EASY
@@
############
#..  #     ###
#..  # $  $  #
#..  #$####  #
#..    @ ##  #
#..  # #  $ ##
###### ##$ $ #
  # $  $ $ $ #
  #    #     #
  ############
TITLE:Level 2:EASY
@@
        ########
        #     @#
        # $#$ ##
        # $  $#
        ##$ $ #
######### $ # ###
#....  ## $  $  #
##...    $  $   #
#....  ##########
########
TITLE:Level 3:EASY
@@
######  ###
#..  # ##@##
#..  ###   #
#..     $$ #
#..  # # $ #
#..### # $ #
#### $ #$  #
   #  $# $ #
   # $  $  #
   #  ##   #
   #########
TITLE:Level 6:EASY
@@
          #######
          #  ...#
      #####  ...#
      #      . .#
      #  ##  ...#
      ## ##  ...#
     ### ########
     # $$$ ##
 #####  $ $ #####
##   #$ $   #   #
#@ $  $    $  $ #
###### $$ $ #####
     #      #
     ########
TITLE:Level 9:MEDIUM
@@
      ####
  #####  #
 ##     $#
## $  ## ###
#@$ $ # $  #
#### ##   $#
 #....#$ $ #
 #....#   $#
 #....  $$ ##
 #... # $   #
 ######$ $  #
      #   ###
      #$ ##
      #  #
      ####
TITLE:Level 32:MEDIUM
@@
 ###########
 #     ##  #
 #   $   $ #
#### ## $$ #
#   $ #    #
# $$$ # ####
#   # # $ ##
#  #  #  $ #
# $# $#    #
#   ..# ####
####.. $ #@#
#.....# $# #
##....#  $ #
 ##..##    #
  ##########
TITLE:Level 33:MEDIUM
@@
        #####
        #   #####
        # #$##  #
        #     $ #
######### ###   #
#....  ## $  $###
#....    $ $$ ##
#....  ##$  $ @#
#########  $  ##
        # $ $  #
        ### ## #
          #    #
          ######
TITLE:Level 5:HARD
@@
    ##########
#####        ####
#     #   $  #@ #
# #######$####  ###
# #    ## #  #$ ..#
# # $  $  #  #  #.#
# # $  #     #$ ..#
# #  ### ##     #.#
# ###  #  #  #$ ..#
# #    # $####  #.#
# #$   $  $  #* ..#
#    $ # $ $ #  #.#
#### $###    #* ..#
   #    $$ ###....#
   #      ## ######
   ########
TITLE:Level 20:HARD
@@
##### ####
#...# #  ####
#...###  $  #
#....## $  $###
##....##   $  #
###... ## $ $ #
# ##    #  $  #
#  ## # ### ####
# $ # #$  $    #
#  $ @ $    $  #
#   # $ $$ $ ###
#  ######  ###
# ##    ####
###
TITLE:Level 45:HARD
"""
# fmt: on

import re

LEVEL_META = []
LEVELS     = []

def _parse_raw(raw):
    blocks = raw.strip().split("@@")
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        title_line = None
        grid_lines = []
        for ln in lines:
            if ln.startswith("TITLE:"):
                title_line = ln
            else:
                grid_lines.append(ln)
        if title_line is None:
            continue
        parts  = title_line.split(":")
        label  = parts[1]   # e.g. "Level 6"
        diff   = parts[2]   # e.g. "EASY"
        # Strip trailing blank rows
        while grid_lines and not grid_lines[-1].strip():
            grid_lines.pop()
        LEVELS.append(grid_lines)
        LEVEL_META.append((label, diff))

_parse_raw(_RAW)


def pad_level(level):
    w = max(len(r) for r in level)
    return [r.ljust(w) for r in level]


def validate_level(level):
    known = set(' #@+$*.')
    players = boxes = goals = 0
    for y, row in enumerate(level):
        for x, ch in enumerate(row):
            if ch not in known:
                return False, f"Unknown '{ch}' at ({x},{y})"
            if ch in ('@', '+'):       players += 1
            if ch in ('$', '*'):      boxes   += 1
            if ch in ('.', '*', '+'): goals   += 1
    if players != 1:
        return False, f"Need 1 player, got {players}"
    if boxes != goals:
        return False, f"Boxes {boxes} != Goals {goals}"
    if boxes == 0:
        return False, "No boxes/goals"
    return True, "OK"


def load_level(i):
    p = pad_level(LEVELS[i])
    ok, msg = validate_level(p)
    if not ok:
        raise ValueError(f"Level {i+1} '{LEVEL_META[i][0]}': {msg}")
    return p