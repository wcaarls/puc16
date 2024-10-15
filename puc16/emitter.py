"""ASM and VHDL emitter for ENG1448 16-bit processor
   (c) 2020-2024 Wouter Caarls, PUC-Rio
"""

# TODO: io section

import os

def emitasmsection(section, f):
    """Emit assembly for a section."""
    addr = 0
    skipped = False
    for c in section:
        if c[1] == '':
            skipped = True
        else:
            if skipped == True:
                print(f'.org {addr}', file=f)
                skipped = False
            print(c[1], file=f)
        addr += 1


def emitasm(mem, f):
    """Emit assembly for all sections."""
    print('.section io', file=f)
    emitasmsection(mem['io'], f)
    print('.section code', file=f)
    emitasmsection(mem['code'], f)
    print('.section data', file=f)
    emitasmsection(mem['data'], f)

def emitarray(section, f, origin):
    """Emit a VHDL array for a section."""
    for l, c in enumerate(section):
        if c[0] != '0000000000000000' or c[1] != '':
            print(f"    {origin+l:4} => \"{c[0]}\", -- {c[1]}", file=f)

def emitvhdl(mem, f, origin):
    """Emit VHDL for all  sections."""
    if f.name != '<stdout>':
        pkg = os.path.splitext(os.path.basename(f.name))[0]
        print(
    f"""library ieee;
use ieee.std_logic_1164.all;

package {pkg} is
  type {pkg}_t is array(0 to 8191) of std_logic_vector(15 downto 0);

  constant {pkg}_init: {pkg}_t := (
""", file=f, end='')
    else:
        pkg = ''
        print(f"""  signal ram: ram_t := (
""", file=f, end='')
    emitarray(mem['io'], f, origin['io'])
    emitarray(mem['code'], f, origin['code'])
    emitarray(mem['data'], f, origin['data'])
    print("  others => (others => '0'));", file=f)

    if pkg != '':
        print(f'end package {pkg};', file=f)
