"""Simulator for ENG1448 16-bit processor
   (c) 2020-2024 Wouter Caarls, PUC-Rio
"""

import array
import copy
from .disassembler import Disassembler

MAXVAL = 65535
NEGBIT = 32768
CARRYBIT = 65536
CODESTART = 16
STACKSTART = 8191
MEMSIZE = 8192+4800

class State:
    """Machine state for simulator."""
    def __init__(self, mem=None,origin=None):
        self.regs = [0 for i in range(16)]

        self.mem = array.array('H', [0 for i in range(MEMSIZE)])
        if mem:
            for s in mem:
                o = origin[s]
                for i, c in enumerate(mem[s]):
                    self.mem[o+i] = int(c[0], 2)

        self.regs[14] = STACKSTART
        self.regs[15] = CODESTART
        self.zero = False
        self.carry = False
        self.negative = False
        self.overflow = False

    def diff(self, state):
        """Calculates difference between this state and another."""
        d = ''

        for i in range(14):
            if self.regs[i] != state.regs[i]:
                d += f', r{i} <- {state.regs[i]}'
        
        for i in range(MEMSIZE):
            if self.mem[i] != state.mem[i]:
                d += f', [{i}] <- {state.mem[i]}'
        
        if self.regs[14] != state.regs[14]:
            d += f', sp <- {state.regs[14]}'
        if self.zero != state.zero:
            d += f', zf <- {state.zero}'
        if self.carry != state.carry:
            d += f', cf <- {state.carry}'
        if self.negative != state.negative:
            d += f', nf <- {state.negative}'
        if self.overflow != state.overflow:
            d += f', vf <- {state.overflow}'

        if d != '':
            d = d[2:]
        return d

    def __str__(self):
        s = ''
        for i in range(14):
            s += f'r{i} = {self.regs[i]}, '
        s += f'pc = {self.regs[15]}, sp = {self.regs[14]}, zf = {self.zero}, cf = {self.carry}, nf = {self.negative}, vf = {self.overflow}'

        return s

class Simulator:
    """Simulates machine code."""
    def __init__(self, map = None):
        self.disassembler = Disassembler(map)

    def execute(self, bin, state):
        """Returns machine state after executing instruction."""
        # Disassemble instruction
        m, dis = self.disassembler.process(bin, state.regs[15])

        opcode = bin[0:4]
        r1 = int(bin[4:8], 2)
        r2 = int(bin[8:12], 2)
        r3 = int(bin[12:16], 2)
        c4i = int(bin[12]*12 + bin[12:16], 2)
        c4 = int(bin[12:16], 2)
        c8i = int(bin[8]*8 + bin[8:16], 2)
        c8 = int(bin[8:16], 2)
        c12 = int(bin[4:16], 2)
        next = copy.deepcopy(state)
        next.regs[15] += 1

        addr = (next.regs[r2] + c4i)&MAXVAL
        if m == 'shft' or ((m == 'add' or m == 'sub') and opcode[3] == '1'):
            val = c4
        else:
            val = state.regs[r3]

        # Simulate instructions
        if m == 'ldr':
            if addr == 2:
                inp = input('Enter keyboard character: ')
                if len(inp) > 0:
                    next.regs[r1] = ord(inp[0])
                else:
                    next.regs[r1] = 0
            else:
                next.regs[r1] = next.mem[addr%MEMSIZE]
        elif m == 'str':
            if addr == 7:
                print(chr(next.regs[r1]), end='')
            elif addr == 8 and next.regs[r1] == 1:
                print()
            else:
                next.mem[addr%MEMSIZE] = next.regs[r1]
        elif m == 'mov':
            if opcode == '0000':
                next.regs[r1] = c8
            else:
                next.regs[r1] = next.regs[r2]
                next.zero = next.regs[r1] == 0
                next.carry = False
                next.negative = bool(next.regs[r1] & NEGBIT)
                next.overflow = False
        elif m == 'movt':
            next.regs[r1] = (next.regs[r1] & 255) + 256*c8
        elif m[0] == 'b':
            # Branches
            if ( m == 'b' or
                (m == 'bz' and state.zero) or (m == 'bnz' and not state.zero) or
                (m == 'bcs' and state.carry) or (m == 'bcc' and not state.carry) or
                (m == 'blt' and (state.overflow != state.negative)) or
                (m == 'bge' and (state.overflow == state.negative))):
                    next.regs[15] = (next.regs[15] + c8i)&MAXVAL
        elif m == 'jmp':
            # Jump
            next.regs[15] = c12
        elif m == 'push':
            if next.regs[14] == -1:
                raise RuntimeError('Stack overflow')
            next.mem[next.regs[14]%MEMSIZE] = next.regs[r3]
            next.regs[14] -= 1
        elif m == 'pop' or m == 'ret':
            if next.regs[14] == STACKSTART:
                raise RuntimeError('Stack underflow')
            next.regs[r1] = state.mem[(next.regs[14]+1)%MEMSIZE]
            next.regs[14] += 1
        else:
            # ALU instructions (modify flags)
            next.overflow = 0
            if m == 'add':
                res = next.regs[r2] + val
                next.overflow = bool((~(next.regs[r2] ^ val) & (next.regs[r2] ^ res)) & NEGBIT)
            elif m == 'sub':
                res = next.regs[r2] + (CARRYBIT-val)
                next.overflow = bool(( (next.regs[r2] ^ val) & (next.regs[r2] ^ res)) & NEGBIT)
            elif m == 'shft':
                amount = (val&7)+1
                if val > 7:
                    # Shift right
                    res = next.regs[r2] >> amount
                else:
                    # Shift left
                    res = next.regs[r2] << amount
            elif m == 'and':
                res = next.regs[r2] & val
            elif m == 'or':
                res = next.regs[r2] | val
            elif m == 'xor':
                res = next.regs[r2] ^ val
            else:
                raise ValueError(f'Unknown opcode {opcode}')

            next.zero = ((res&MAXVAL) == 0)
            next.carry = bool(res & CARRYBIT)
            next.negative = bool(res & NEGBIT)
            next.regs[r1] = res&MAXVAL

        return next

    def help(self):
        print("""Available commands:
   h       This help.
   n       Advance to next instruction.
   b a     Set or clear breakpoint at address a.
   c       Execute continuously until halted.
   p       Print current state.
   q       Exit simulator.
   rx      Print contents of register x.
   rx = y  Set register x to value y.
   [a]     Print contents of memory address a.
   [a] = y Set memory address a to value y.
""")

    def process(self, mem, origin):
        """Simulate machine code."""
        state = State(mem, origin)

        breakpoints = []
        quiet = False

        while True:
            # Print current instruction
            bin = format(state.mem[state.regs[15]], '016b')

            if quiet:
                next = self.execute(bin, state)
                if next.regs[15] == state.regs[15] or next.regs[15] in breakpoints:
                    quiet = False
                state = next
                continue

            _, dis = self.disassembler.process(bin, state.regs[15])
            print(f'{state.regs[15]:3}: {bin[0:4]} {bin[4:8]} {bin[8:12]} {bin[12:16]} ({dis})')

            next = copy.deepcopy(state)

            # Present interface
            cmd = input('>> ').strip()
            if cmd == '' or cmd == 'n':
                # Advance to next instruction
                next = self.execute(bin, state)
            elif cmd == 'c':
                # Execute continuously
                quiet = True
            elif cmd[0] == 'b':
                # Set (or clear) breakpoint
                try:
                    line = int(cmd[2:], 0)
                    if line in breakpoints:
                        breakpoints.remove(line)
                    else:
                        breakpoints.append(line)
                    print('breakpoints: ', breakpoints)
                except Exception as e:
                    print(e)
            elif cmd == 'p':
                # Print current state
                print(state)
            elif cmd == 'q':
                # Exit simulator
                return
            elif cmd[0] == 'r':
                # Set register
                tokens = [t.strip() for t in cmd.split('=')]
                if len(tokens[0]) < 2:
                    self.help()
                elif len(tokens) == 1:
                    try:
                        print(f'r{int(tokens[0][1:])} = {state.regs[int(tokens[0][1:])]}')
                    except Exception as e:
                        print(e)
                elif len(tokens) == 2:
                    try:
                        next.regs[int(tokens[0][1:])] = int(tokens[1], 0)&MAXVAL
                    except Exception as e:
                        print(e)
                else:
                    self.help()
            elif cmd[0] == '[':
                # Set memory address
                tokens = [t.strip() for t in cmd.split('=')]
                if len(tokens[0]) < 2 or tokens[0][0] != '[' or tokens[0][-1] != ']':
                    self.help()
                elif len(tokens) == 1:
                    try:
                        print(f'[{int(tokens[0][1:-1])}] = {state.mem[int(tokens[0][1:-1])]}')
                    except Exception as e:
                        print(e)
                elif len(tokens) == 2:
                    try:
                        next.mem[int(tokens[0][1:-1])] = int(tokens[1], 0)&MAXVAL
                    except Exception as e:
                        print(e)
                else:
                    self.help()
            else:
                self.help()

            # Print resulting difference
            diff = state.diff(next)
            if diff != '':
                print('     ' + diff)
            state = copy.deepcopy(next)

    def run(self, mem, origin, steps=1000):
        """Simulate machine code for a set number of steps and return PC."""
        state = State(mem, origin)

        for s in range(steps):
            bin = format(state.mem[state.regs[15]], '016b')
            state = copy.deepcopy(self.execute(bin, state))

        return state.regs[15]
