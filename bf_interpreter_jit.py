#!/usr/bin/env python
# -*- coding: utf-8 -*-
# From https://github.com/wdv4758h/brainfuck_bench repo, this is example7.py
# version 7, optimize case that loop to zero

import os
import time
# So that you can still run this module under standard CPython, I add this
# import guard that creates a dummy class instead.
try:
    from rpython.rlib.jit import JitDriver, elidable
except ImportError:
    class JitDriver(object):
        def __init__(self,**kw): pass
        def jit_merge_point(self,**kw): pass
        def can_enter_jit(self,**kw): pass
    def elidable(f): return f

try:
    from rpython.rlib.rstring import replace
except ImportError:
    def replace(string, old, new):
        return string.replace(old, new)

def get_location(pc, program, bracket_map):
    return "%s_%s_%s" % (
        program[:pc], program[pc], program[pc+1:]
    )

jitdriver = JitDriver(
                greens=['pc', 'program', 'bracket_map'],
                reds=['tape'],
                get_printable_location=get_location,
            )

@elidable
def get_matching_bracket(bracket_map, pc):
    return bracket_map[pc]

class Tape(object):
    def __init__(self):
        self.thetape = [0]
        self.position = 0
        self.output = ''
        self.output_threshold = 50

    def get(self):
        return self.thetape[self.position]

    def set(self, val):
        self.thetape[self.position] = val

    def inc(self):
        self.thetape[self.position] += 1

    def dec(self):
        self.thetape[self.position] -= 1

    def advance(self):
        self.position += 1
        if len(self.thetape) <= self.position:
            self.thetape.append(0)

    def devance(self):
        self.position -= 1

    def clear(self):
        if self.output:
            os.write(1, self.output)    # 1 for stdout
            self.output = ''

    def read(self):
        self.clear()

        data = os.read(0, 1)    # 0 for stdin, 1 for one byte

        if data:
            self.set(ord(data[0]))

    def write(self):
        self.output += chr(self.get())

        if len(self.output) > self.output_threshold:
            os.write(1, self.output)    # 1 for stdout
            self.output = ''

def main_loop(program, bracket_map):
    pc = 0
    tape = Tape()

    while pc < len(program):
        jitdriver.jit_merge_point(pc=pc, tape=tape, program=program, bracket_map=bracket_map)

        code = program[pc]

        if code == ">":
            tape.advance()

        elif code == "<":
            tape.devance()

        elif code == "+":
            tape.inc()

        elif code == "-":
            tape.dec()

        elif code == ".":
            # print
            tape.write()

        elif code == ",":
            # read from stdin
            tape.read()

        elif code == "[" and tape.get() == 0:
            # Skip forward to the matching ]
            pc = get_matching_bracket(bracket_map, pc)

        elif code == "]" and tape.get() != 0:
            # Skip back to the matching [
            pc = get_matching_bracket(bracket_map, pc)

        elif code == "0":
            tape.set(0)
            pc += 2

        pc += 1
    tape.clear()

def zero(program):
    return replace(program, '[-]', '000')    # use three '0' to keep pc, so bracket_map won't broke

def parse(program):
    parsed = []
    bracket_map = {}
    leftstack = []

    pc = 0
    for char in program:
        if char in ('[', ']', '<', '>', '+', '-', ',', '.'):
            parsed.append(char)

            if char == '[':
                leftstack.append(pc)
            elif char == ']':
                left = leftstack.pop()
                right = pc
                bracket_map[left] = right
                bracket_map[right] = left
            pc += 1

    return ''.join(parsed), bracket_map

def run(input_file):

    with open(input_file, 'r') as f:
        program, bracket_map = parse(f.read())

    # optimize
    program = zero(program)
    start = time.time()
    main_loop(program, bracket_map)
    elapsed = time.time() - start
    print(elapsed)

def entry_point(argv):
    if len(argv) > 1:
        filename = argv[1]
    else:
        print("You must supply a filename")
        return 1

    run(filename)
    return 0

def target(*args):
    return entry_point

if __name__ == "__main__":
    import sys
    entry_point(sys.argv)
