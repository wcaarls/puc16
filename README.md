# PUC16

Assembler and C compiler for the PUC16 processor

Copyright 2020-2024 Wouter Caarls

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Introduction

PUC16 is a microcontroller with 16 opcodes and 16 16-bit registers.
It is used in the ENG1448 course of PUC-Rio. This is the assembler and
C compiler infrastructure for it.

# Instruction set architecture

This very simple processor is a Von Neumann design, with 16-bit instructions and 16-bit data words. It does not support byte addressing.

## Registers

There are 16 registers. `r14` is `sp`; `r15` is `pc`. The C compiler uses `r13` as `fp`. `r12` is often used as a temporary register.

## Instructions

All ALU instructions set flags.

| Group(2) | Op(2) | Nibble 1(4) | Nibble 2(4) | Nibble 3(4) | Mnm | Effect | Example |
|---|---|---|---|---|---|---|---|
| 00 | 00 | rd          | c8u(7..4)  | c8u(3..0)  | MOV  | rd <- c8u                       | `mov  r0, 254`        |
| 00 | 01 | rd          | c8u(7..4)  | c8u(3..0)  | MOVT | rd <- (rd&255) \| (c8u<<8)      | `movt r0, 254`        |
| 00 | 10 | cond        | c8i(7..4)  | c8i(3..0   | B... | if cond then pc <- pc + c8i + 1 | `b    -4`             |
| 00 | 11 | c12u(11..8) | c12u(7..4) | c12u(3..0) | JMP  | pc <- c12u                      | `jmp  2543`           |
| 01 | 00 | rd          | rs         | c4i        | LDR  | rd <- [rs + c4i]                | `ldr  r0, [r1, 4]`    |
| 01 | 01 | rs1         | rs2        | c4i        | STR  | [rs2 + c4i] <- rs1              | `str  r0, [r1, 4]`    |
| 01 | 10 | 0000        | 1110       | rs         | PUSH | [sp] <- rs, sp <- sp - 1        | `push r0`             |
| 01 | 11 | rd          | 1110       | 0000       | POP  | rd <- [sp + 1], sp <- sp + 1    | `pop  r0`             |
| 10 | 00 | rd          | rs1        | rs2        | ADD  | rd <- rs1 + rs2                 | `add  r0, r1, r2`     |
| 10 | 01 | rd          | rs1        | c4u        | ADD  | rd <- rs1 + c4u                 | `add  r0, r1, 5`      |
| 10 | 10 | rd          | rs1        | rs2        | SUB  | rd <- rs1 - rs2                 | `sub  r0, r1, r2`     |
| 10 | 11 | rd          | rs1        | c4u        | SUB  | rd <- rs1 - c4u                 | `sub  r0, r1, 13`     |
| 11 | 00 | rd          | rs1        | 0 c3u      | SHFT | rd << (c3u+1)                   | `shft r0, r1, 8`[^1]  |
| 11 | 00 | rd          | rs1        | 1 c3u      | SHFT | rd >> (c3u+1)                   | `shft r0, r1, -3`[^2] |
| 11 | 01 | rd          | rs1        | rs2        | AND  | rd <- rs1 & rs2                 | `and  r0, r1, r2`     |
| 11 | 10 | rd          | rs1        | rs2        | OR   | rd <- rs1 \| rs2                | `or   r0, r1, r2`     |
| 11 | 11 | rd          | rs1        | rs2        | XOR  | rd <- rs1 ^ rs2                 | `xor  r0, r1, r2`     |

[^1]: May be implemented as a constant shift left of 1.
[^2]: May be implemented as a constant shift right of 1.

`c4i` can be omitted from the assembly instruction, in which case it is set to 0.

## Pseudo-instructions

| Pseudo-instruction | Actual instruction |
|---|---|
| `beq` | `bz` |
| `bne` | `bnz` |
| `bhs` | `bcs` |
| `blo` | `bcc` |
| `ret` | `pop pc` |
| `jmp r0` | `mov pc, r0` |
| `mov r0, r1` | `add r0, r1, 0` |

## Condition codes

| Condition | Mnemonic | Meaning |
|---|---|---|
| 0000 |    | Unconditional                |
| 0001 | z  | Zero flag set                |
| 0010 | nz | Zero flag not set            |
| 0011 | cs | Carry flag set               |
| 0100 | cc | Carry flag not set           |
| 0101 | lt | Signed less than             |
| 0110 | ge | Signed greater than or equal |

# Assembly language

Assembly statements generally follow the following structure
```asm
[LABEL:] MNEMONIC [OPERAND[, OPERAND]...]
```
The available `MNEMONIC`s can be found in the table above. `OPERAND`s can be registers, constants, or labels. Labels used as operands must be prefixed with `@`:
```asm
loop: jmp @loop
```
When the operand is used as the contents of a memory address, it must be enclosed in square brackets:
```asm
ldr r0, [r12]
.section data
inp: .dw 0
```
Apart from these statements, the assembler recognizes the following directives:

- ```asm
  .include "FILE"
  ```

  Includes a given `FILE`. The path is relative to the file being processed.

- ```asm
  .section SECTION
  ```

  Define into which memory `SECTION` the subsequent code is assembled. Options are `code` and `data`. The default is `code`.

- ```asm
  .org ADDRESS
  ```

  Sets memory `ADDRESS` at which the subsequent code will be assembled.

- ```asm
  .equ LABEL VALUE
  ```

  Creates a `LABEL` for a specific constant `VALUE`. Values may be character constants, e.g. `"c"`

- ```asm
  .dw VALUE
  ```

  Inserts a `VALUE` into the instruction stream. The value may be a string constant, e.g. `"Hello, world"`

- ```asm
  .macro NAME
  ; code
  .endmacro
  ```

  Defines a macro. The code inside the macro can use arguments of the form `$0`, `$1`, etc., which are replaced by the actual arguments when the macro is called using `NAME arg0, arg1`. Labels inside the macro that start with an underscore are localized such that the same macro can be called multiple times.

# Installation

```
pip install puc16
```

or

```
git clone https://github.com/wcaarls/puc16
cd puc16
pip install .
```

# Usage

```
usage: as-puc16 [-h] [-o OUTPUT] [-s] [-t N] [-E] file

PUC16 Assembler (c) 2020-2024 Wouter Caarls, PUC-Rio

positional arguments:
  file                  ASM source file

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file
  -s, --simulate        Simulate resulting program
  -t N, --test N        Simulate for 1000 steps and check whether PC == N
  -E                    Output preprocessed assembly code

```

```
usage: cc-puc16 [-h] [-o OUTPUT] [-s] [-t N] [-S] [-O {0,1,2}] file

PUC16 C compiler (c) 2020-2024 Wouter Caarls, PUC-Rio

positional arguments:
  file                  C source file

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file
  -s, --simulate        Simulate resulting program
  -t N, --test N        Simulate for 1000 steps and check whether PC == N
  -S                    Output assembly code
  -O {0,1,2}            Optimization level

```

# Examples

Directly compile C to VHDL
```
./cc-puc16 examples/c/hello.c
```

Create assembly from C
```
./cc-puc16 examples/c/hello.c -S
```

Assemble to VHDL code
```
./as-puc16 examples/asm/ps2_lcd.asm
```

Assemble to VHDL package
```
./as-puc16 examples/asm/ps2_lcd.asm -o ps2_lcd.vhdl
```

Simulate resulting C or assembly program
```
./cc-puc16 -O0 examples/c/unittest.c -s
./as-puc16 examples/asm/simple.asm -s
```

# Acknowledgments

The C compiler is based on [PPCI](https://github.com/windelbouwman/ppci).

Copyright (c) 2011-2019, Windel Bouwman

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
